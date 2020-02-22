# Analysis of spleeter time frame width ('T') parameter

The goal is to use the [musDB18](https://zenodo.org/record/1117372#.XkxbIhNKjVo)
database to train the [spleeter](https://github.com/deezer/spleeter) network and
analyze the influence of the time frame width parameter.

We will test this for both 2 and 4 stems (musdb only provides 4stems). And for
values of T in `[16, 32, 64, 128, 256, 512, 1024]`.

The outcome of this study will determine whether or not we can use the spleeter
architecture on real time application (the parameter express the most of what
will become the latency).

### Using `musDB18` in `Spleeter`

the database is exported as stem files but a
[this](https://github.com/sigsep/sigsep-mus-db) can be used to convert it to
regular wav. The `dbpath` input parameter of `train.py` is the path to the
converted database.

### Running on AWS Deep Learning AMI (Ubuntu18.04)

Boot the AMI with a role that allows s3 access.
Copy the database (I uploaded it to S3 first)
```
aws s3 cp s3://gvne-database/musdb18-converted musdb18-converted --recursive
```

activate the right environment and install dependencies
```
source activate tensorflow_py36
conda install -y ffmpeg
pip install ffmpeg-python ffprobe
```
Note: use ffmpeg-python instead of ffmpeg as [described](https://github.com/deezer/spleeter/issues/101)

clone the right repositories:
```
git clone https://github.com/gvne/spleeter_train_parameters.git
git clone https://github.com/deezer/spleeter.git
ln -s spleeter/spleeter spleeter_train_parameters/spleeter
cd spleeter_train_parameters
```

Start the learning
```
python train.py --dbpath ../musdb18-converted
```

### NOTE: Error when using tensorflow 1.15:
```
NotImplementedError: in converted code:
    relative to /Users/gvne:

    code/github/spleeter_time_frame_width/spleeter/dataset.py:134 compute_spectrogram  *
        return dict(sample, **{
    code/github/spleeter_time_frame_width/spleeter/audio/spectrogram.py:47 compute_spectrogram_tf  *
        return np.abs(stft_tensor) ** spec_exponent
    miniconda3/envs/sptest/lib/python3.6/site-packages/tensorflow_core/python/framework/ops.py:736 __array__
        " array.".format(self.name))

    NotImplementedError: Cannot convert a symbolic Tensor (transpose_1:0) to a numpy array.
```

To avoid that problem, you can use an older version of the AWS deep learning AMI
which ships with tensorflow 1.14 (I used version 24: ami-004852354728c0e51).

## Credits

We use `musDB18` for our tests:
```
@misc{MUSDB18,
  author       = {Rafii, Zafar and
                  Liutkus, Antoine and
                  Fabian-Robert St{\"o}ter and
                  Mimilakis, Stylianos Ioannis and
                  Bittner, Rachel},
  title        = {The {MUSDB18} corpus for music separation},
  month        = dec,
  year         = 2017,
  doi          = {10.5281/zenodo.1117372},
  url          = {https://doi.org/10.5281/zenodo.1117372}
}
```

And rely on `spleeter` to vary the parameter
```
@misc{spleeter2019,
  title={Spleeter: A Fast And State-of-the Art Music Source Separation Tool With Pre-trained Models},
  author={Romain Hennequin and Anis Khlif and Felix Voituret and Manuel Moussallam},
  howpublished={Late-Breaking/Demo ISMIR 2019},
  month={November},
  note={Deezer Research},
  year={2019}
}
```
