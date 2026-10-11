from command import Command


class CommandQueue:
    def __init__(self):
        self._commands: list[Command] = []

    def add(self, command: Command):
        self._commands.append(command)

    def run_all(self):
        for command in self._commands:
            command.execute()
