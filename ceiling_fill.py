import os
from datetime import datetime

import numpy
from amulet import Block, SelectionBox
from typing import TYPE_CHECKING, Tuple, Dict
import wx
from amulet.api.partial_3d_array.base_partial_3d_array import BasePartial3DArray

from amulet_map_editor.api.wx.ui.base_select import EVT_PICK
from amulet_map_editor.api.wx.ui.block_select import BlockDefine
from amulet_map_editor.programs.edit.api.operations import DefaultOperationUI

if TYPE_CHECKING:
    from amulet.api.level import BaseLevel
    from amulet_map_editor.programs.edit.api.canvas import EditCanvas


def _check_block(block: Block, original_base_name: str,
                 original_properties: Dict[str, "WildcardSNBTType"]) -> bool:
    if (block.base_name == original_base_name
            and all(
                original_properties.get(prop) in ["*", val.to_snbt()]
                for prop, val in block.properties.items()
            )
    ):
        return True
    return False


class CeilingFill(wx.Panel, DefaultOperationUI):
    def __init__(
            self, parent: wx.Window, canvas: "EditCanvas", world: "BaseLevel", options_path: str
    ):
        wx.Panel.__init__(self, parent)
        DefaultOperationUI.__init__(self, parent, canvas, world, options_path)

        self.Freeze()
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self._sizer)

        options = self._load_options({})

        self._description = wx.TextCtrl(
            self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_BESTWRAP, size=(200, 100)
        )
        self._sizer.Add(self._description, 0, wx.ALL | wx.EXPAND, 5)
        self._description.SetLabel("ワールドの全ディメンションのY255に指定したブロックを敷き詰めます")
        self._description.Fit()

        self._block_define = BlockDefine(
            self,
            world.translation_manager,
            wx.VERTICAL,
            *(options.get("fill_block_options", []) or [world.level_wrapper.platform]),
            show_pick_block=True
        )
        self._block_define.Bind(EVT_PICK, self._on_pick_block_button)
        self._sizer.Add(self._block_define, 1, wx.ALL | wx.ALIGN_CENTRE_HORIZONTAL, 5)

        self._run_button = wx.Button(self, label="実行")
        self._run_button.Bind(wx.EVT_BUTTON, self._run_operation)
        self._sizer.Add(self._run_button, 0, wx.ALL | wx.ALIGN_CENTRE_HORIZONTAL, 5)

        self.Layout()
        self.Thaw()

    @property
    def wx_add_options(self) -> Tuple[int, ...]:
        return (1,)

    def _on_pick_block_button(self, evt):
        self._show_pointer = True

    def disable(self):
        print("Unload CeilingFill")

    def _run_operation(self, _):
        self.canvas.run_operation(
            lambda: self._ceiling_fill()
        )

    def _get_fill_block(self) -> Block:
        return self._block_define.universal_block[0]

    def _ceiling_fill(self):
        world = self.world
        chunk_count = 0
        count = 0
        (
            fill_platform,
            fill_version,
            fill_blockstate,
            fill_namespace,
            fill_base_name,
            fill_properties,
        ) = (
            self._block_define.platform,
            self._block_define.version_number,
            self._block_define.force_blockstate,
            self._block_define.namespace,
            self._block_define.block_name,
            self._block_define.str_properties,
        )

        fill_block = self._get_fill_block()

        # 全てのディメンションのチャンク数を取得
        for dimension in world.dimensions:
            chunk_count += len(list(world.all_chunk_coords(dimension)))

        for dimension in world.dimensions:
            for cx, cz in world.all_chunk_coords(dimension):
                chunk = world.get_chunk(cx, cz, dimension)

                for dx in range(16):
                    for dz in range(16):
                        chunk.set_block(dx, 255, dz, fill_block)

                chunk.changed = True

                count += 1
                yield count / chunk_count




export = {
    "name": "天井敷き詰め",  # the name of the plugin
    "operation": CeilingFill,  # the actual function to call when running the plugin
}
