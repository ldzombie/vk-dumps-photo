class ErrorLog:
    log_file = "errors.log"

    def __init__(self):
        self.errors = []

    def add(self, module, error):
        self.errors.append(f'{module} - {error}')

    def error_list(self):
        return self.errors

    def save_log(self):
        if self.errors and self.log_file:
            with open(self.log_file, 'w') as error_log_file:
                for error in self.errors:
                    error_log_file.write(f'{error}\n')


def add_error(val1: str):
    with open(ErrorLog().log_file, 'w+') as file:
        file.write(f"{val1}\n")
