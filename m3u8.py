class M3U8:
    def __init__(self, abs_path):
        self.abs_path = abs_path

    def get_contents(self, i):
        with open(self.abs_path, "r") as f:
            return f.readlines()[0:i]
        return None

    def get_number_of_line(self):
        with open(self.abs_path, "r") as f:
            return len(f.readlines())
        return 0
    
    def create_from_contents(self, contents):
        with open(self.abs_path, 'w') as f:
            for line in contents:
                f.write(line)

    def append_end(self, line):
        with open(self.abs_path, 'rb+') as f:
            f.seek(-1, 2)
            f.write((line + "\n").encode())