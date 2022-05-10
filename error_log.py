class ErrorLog:
    def __init__(self):
        self.errors = []

    def add(self, module, error):
        self.errors.append(f'{module} - {error}')

    def error_list(self):
        return self.errors

    def save_log(self, filename='errors.log'):
        if self.errors and filename:
            with open(filename, 'w') as error_log_file:
                for error in self.errors:
                    error_log_file.write(f'{error}\n')
