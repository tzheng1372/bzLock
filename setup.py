from setuptools import setup

setup(name="bzLock",
      version="1.0",
      description="bzLock Library",
      author="Jason Pei, Thomas Zheng",
      author_email="peijiannuo@gmail.com, tz1372@nyu.edu",
      url="https://github.com/tzheng1372/bzLock",
      install_requires=["adafruit-python-shell", "pigpio", "spidev",
                        "adafruit-circuitpython-matrixkeypad", "hx711", "luma.oled"],
      py_modules=["bzLock"],
      )
