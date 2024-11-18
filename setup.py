from setuptools import setup, find_packages

setup(
    name='pdf-cropper',  # 项目名称
    version='0.1',  # 版本号
    description='A Python tool to crop PDF pages by removing headers, footers, and margins.',
    author='Your Name',  # 你的名字
    author_email='your_email@example.com',  # 你的邮件地址
    packages=find_packages(),  # 自动发现和打包你的项目中的所有模块
    install_requires=[  # 依赖项，列出所有依赖的库和版本
        'PyMuPDF==1.19.6', 
        'Pillow==9.5.0'
    ],
    entry_points={  # 这个指定了当用户运行 `pdf-cropper` 时将执行的函数
        'console_scripts': [
            'pdf-cropper=pdf_cropper:main',  # 你需要在 pdf_cropper.py 中定义一个 main 函数
        ],
    },
    include_package_data=True,  # 将非 Python 文件包含在包内
    classifiers=[  # 分类器可以让 PyPI 更好地识别和分类
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',  # 指定项目支持的最低 Python 版本
)
