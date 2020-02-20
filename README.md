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

the database is exported as stem files. However, to train spleeter we need
single wav files and a CSV describing it. the `musdb.py` script can be used to
format the database and export the desired CSVs

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
