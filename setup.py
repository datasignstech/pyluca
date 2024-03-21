import setuptools

setuptools.setup(
    name='pyluca',
    version='2.6.0',
    author='datasignstech',
    author_email='tech+opensource@datasignstech.com',
    description='Double entry accounting system',
    url='https://github.com/datasignstech/pyluca',
    packages=['pyluca'],
    include_package_data=True,
    long_description='A headless python Double Entry Accounting package',
    long_description_content_type='text/plain',
    install_requires=[r for r in open('requirements.txt', 'r').read().split('\n') if r]
)
