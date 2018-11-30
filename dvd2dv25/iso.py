import os
import isoparser


class Extractor:
    """
    Extracts files from an iso file

    Examples:

        iso_extractor = Extractor("my_video_image.iso")
        with iso_extractor as e:
            for path_name, compressed_file in e:
                dst = os.path.dirname(os.path.join(root_dir, path_name))
                e.extract(compressed_file, dest=dst)
    """
    def __init__(self, filename) -> None:
        self._filename = filename

    def __iter__(self):
        for f in self._iso.root.children:

            for i in self._list(f):
                yield i

    def __enter__(self):
        self._iso = isoparser.parse(self._filename)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._iso.close()

    def _list(self, item, starting_directory=""):

        new_item_path = os.path.join(starting_directory, str(item.name, encoding="utf-8"))
        if item.is_directory:
            yield starting_directory, item

            for i in item.children:
                for new_item_path_file, child_record in self._list(i, new_item_path):
                    yield new_item_path_file, child_record

        else:
            yield new_item_path, item

    def extract(self, record, dest):
        new_item = os.path.join(dest, str(record.name, encoding="utf-8"))
        if record.is_directory:
            os.makedirs(new_item, exist_ok=True)
        else:
            with open(new_item, "wb") as fw:
                fw.write(record.content)
