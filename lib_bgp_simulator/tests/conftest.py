from .utils import YamlSystemTestRunner


# https://stackoverflow.com/a/66597438/8903959
def pytest_addoption(parser):
    parser.addoption(YamlSystemTestRunner.write_no_verify_arg,
                     action="store_true",
                     default=False)
    parser.addoption(YamlSystemTestRunner.view_arg,
                     action="store_true",
                     default=False)
    parser.addoption(YamlSystemTestRunner.debug_arg,
                     action="store_true",
                     default=False)
