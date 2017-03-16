import os

def job_chdir(func):
    def func_wrapper(job, **kwargs):
        cwd = os.getcwd()
        os.chdir(job.workspace())
        func(job, **kwargs)
        os.chdir(cwd)
    return func_wrapper
