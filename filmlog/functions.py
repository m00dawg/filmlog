from filmlog import app

# Functions
def result_to_dict(result):
    return [dict(row) for row in result]
