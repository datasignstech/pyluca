import setuptools

setuptools.setup(
    name='pyluca',
    version='0.0.0',
    author='datasignstech',
    author_email='pramod.kumar@datasignstech.com',
    description='Double entry accounting system',
    url='https://github.com/datasignstech/pyluca',
    packages=['pyluca'],
    include_package_data=True,
    long_description='A headless python Double Entry Accounting package',
    long_description_content_type='text/plain',
    install_requires=[
        'pandas==1.1.5',
        'pydictable==0.9.4'
    ]
)
