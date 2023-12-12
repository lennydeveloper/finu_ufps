def secure_filename(filename):
    idx = filename.rfind('.')

    def safe_char(c):
        if c.isalnum():
            return c
        else:
            return "_"

    return "".join(safe_char(c) for c in filename[0:idx]).rstrip("_").lower() + filename[idx:len(filename)]
