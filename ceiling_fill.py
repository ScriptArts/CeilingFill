import amulet
import numpy
from amulet.api.block import Block


def _main():
    chunk_count = 0
    count = 0

    print("ワールドのディレクトリパスを入力してください。")
    directory = input()
    world = amulet.load_level(directory)

    all_dimension_name = ""
    # 処理を除外するディメンションの選択
    for dimension in world.dimensions:
        all_dimension_name += dimension + " "

    print("このワールドの全ディメンション名")
    print(all_dimension_name)
    print("処理を除外したいディメンションがある場合は、ディメンション名を入力してください。")
    print("複数ある場合はカンマ「,」区切りで入力してください。")
    exclude_dimension = input()
    exclude_dimension_list = exclude_dimension.split(",")

    print("敷き詰めるブロックを入力してください。 例 minecraft:water[level=0]")
    fill_block_str = input()
    fill_block = Block.from_string_blockstate(fill_block_str)

    print("ブロックを敷き詰めるY座標を入力してください。")
    y_pos = int(input())

    # 全てのディメンションのチャンク数を取得
    for dimension in world.dimensions:
        if dimension not in exclude_dimension_list:
            chunk_count += len(list(world.all_chunk_coords(dimension)))

    print("ブロック削除プラグイン実行")
    print("総検索チャンク数:" + str(chunk_count))
    print("----------開始----------")

    for dimension in world.dimensions:
        if dimension in exclude_dimension_list:
            continue

        for cx, cz in world.all_chunk_coords(dimension):
            chunk = world.get_chunk(cx, cz, dimension)

            for dx in range(16):
                for dz in range(16):
                    chunk.set_block(dx, y_pos, dz, fill_block)

            chunk.changed = True
            count += 1

            print(dimension + " " + str(count) + "/" + str(chunk_count))

            if count % 1000 == 0:
                print("途中経過を保存中...")
                world.save()
                world.purge()

    world.save()
    world.close()
    print("----------終了----------")
    return 0


if __name__ == '__main__':
    _main()
