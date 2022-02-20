from django.db import models


class Movie(models.Model):
    def __str__(self):
        return self.imdbid

    title = models.CharField(max_length=300)
    rated = models.CharField(max_length=50)
    released = models.DateField(null=True)
    runtime = models.CharField(max_length=50)
    genre = models.CharField(max_length=200)
    director = models.CharField(max_length=100)
    writer = models.TextField()
    actors = models.TextField()
    plot = models.TextField()
    language = models.CharField(max_length=100)
    country = models.CharField(max_length=50)
    awards = models.TextField()
    poster = models.URLField()
    metascore = models.IntegerField()
    imdbrating = models.DecimalField(max_digits=2, decimal_places=1)
    imdbvotes = models.IntegerField()
    imdbid = models.CharField(max_length=50)
    type = models.CharField(max_length=50)
    dvd = models.DateField(null=True)
    boxoffice = models.IntegerField()
    production = models.CharField(max_length=100)
    website = models.URLField()

    @classmethod
    def get_all(cls):
        return cls.objects.all()
