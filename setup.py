import setuptools

if __name__ == "__main__":

    with open('requirements.txt', 'r') as f:
        requirements = f.readlines()
        requirements = [line.strip() for line in requirements if line.strip()]

    setuptools.setup(name = 'ult_instruments',
    version = '3.2.1',
    author = 'Dillon Wong',
    author_email = '',
    description = 'Controls ULT instrumentation.',
    url = 'https://github.com/dilwong/ult_instruments',
    install_requires = requirements,
    packages=['ult_instruments'],
    package_dir={'ult_instruments': 'Python'}
    )