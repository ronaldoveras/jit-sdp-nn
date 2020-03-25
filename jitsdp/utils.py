def mkdir(dir):
    dir.mkdir(parents=True, exist_ok=True)


def split_arg(argv, name):
    try:
        value_index = argv.index(name) + 1
    except ValueError:  # argument not in list
        return argv
    value = argv[value_index]
    return argv[:value_index] + value.split() + argv[value_index + 1:]

def split_args(argv, names):
    new_argv = argv
    for name in names:
        new_argv = split_arg(new_argv, name)
    return new_argv