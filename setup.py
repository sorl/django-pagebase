from setuptools import setup, find_packages


setup(
    name='django-pagebase',
    version='0.3',
    description='Pages for Django',
    long_description=open('README.rst').read(),
    author='Mikko Hellsing',
    author_email='mikko@aino.se',
    license='BSD',
    url='https://github.com/aino/django-pagebase',
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['django-aislug>=0.1'],
    zip_safe=False,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Framework :: Django',
    ],
)

