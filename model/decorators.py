"""
Set of decorators for model data presentation
"""
def data_func(method):
    method.wrapped = True
    return method
