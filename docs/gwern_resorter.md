---
title: Resorting Media Ratings
description: Commandline tool providing interactive statistical pairwise ranking and sorting of items
created: 2015-09-07
modified: 2018-08-15
status: finished
confidence: likely
importance: 3
css-extension: dropcaps-yinit
...

<div class="abstract">
> User-created datasets using ordinal scales (such as media ratings) have tendencies to drift or 'clump' towards the extremes and fail to be informative as possible, falling prey to ceiling effects and making it difficult to distinguish between the mediocre & excellent.
>
> This can be counteracted by rerating the dataset to create a uniform (and hence, informative) distribution of ratings---but such manual rerating is difficult.
>
> I provide an anytime CLI program, `resorter`, written in R (should be cross-platform but only tested on Linux) which keeps track of comparisons, infers underlying ratings assuming that they are noisy in the ELO-like Bradley-Terry model, and interactively & intelligently queries the user with comparisons of the media with the most uncertain current ratings, until the user ends the session and a fully rescaled set of ratings are output.
</div>

**Resorter** reads in a CSV file of names (with an optional second column of ratings), and then, with a number of options, will ask the user about specific comparisons until such time as the user decides that the rankings are probably accurate enough (unlike standard comparison sorts, the comparisons are allowed to be noisy!), and quits the interactive session, at which point the underlying rankings are inferred and a uniformly-distributed re-ranked set of ratings are printed or written out.

# Use

Available features:

~~~{.Bash}
$ ./resorter --help
# usage: resorter [--help] [--verbose] [--no-scale] [--no-progress] [--opts OPTS] [--input INPUT] [--output OUTPUT] [--queries QUERIES]
#                 [--levels LEVELS] [--quantiles QUANTILES]
#
# sort a list using comparative rankings under the Bradley-Terry statistical model; see https://gwern.net/resorter
#
#
# flags:
#   -h, --help            show this help message and exit
#   -v, --verbose         whether to print out intermediate statistics
#   --no-scale           Do not discretize/bucket the final estimated latent ratings into 1-l levels/ratings; print out inferred latent scores.
#   --no-progress         Do not print out mean standard error of items
#
# optional arguments:
#   -x, --opts OPTS           RDS file containing argument values
#   -i, --input INPUT         input file: a CSV file of items to sort: one per line, with up to two columns. (eg. both 'Akira\n' and 'Akira, 10\n' are valid).
#   -o, --output OUTPUT           output file: a file to write the final results to. Default: printing to stdout.
#   -n, --queries QUERIES         Maximum number of questions to ask the user; if already rated, 𝒪(items) is a good max, but the more items and more levels in
#                                 the scale, the more comparisons are needed. [default: 2147483647]
#   -l, --levels LEVELS            The highest level; rated items will be discretized into 1-l levels, so l=5 means items are bucketed into 5 levels: [1,2,3,4,5],
#                                  etc [default: 5]
#   -q, --quantiles QUANTILES         What fraction to allocate to each level; space-separated; overrides `--levels`. This allows making one level of ratings
#                                     narrower (and more precise) than the others, at their expense; for example, one could make 3-star ratings rarer with quantiles
#                                      like `--quantiles '0 0.25 0.8 1'`. Default: uniform distribution (1--5 → '0.0 0.2 0.4 0.6 0.8 1.0').
~~~

Here is an example demonstrating the use of `resorter` to have the user make 10 comparisons, rescale the scores into 1--3 ratings (where 3 is rare), and write the new rankings to a file:

~~~{.Bash .collapse}
$ cat anime.txt
# "Cowboy Bebop", 10
# "Monster", 10
# "Neon Genesis Evangelion: The End of Evangelion", 10
# "Gankutsuou", 10
# "Serial Experiments Lain", 10
# "Perfect Blue", 10
# "Jin-Rou", 10
# "Death Note", 10
# "Last Exile", 9
# "Fullmetal Alchemist", 9
# "Gunslinger Girl", 9
# "RahXephon", 9
# "Trigun", 9
# "Fruits Basket", 9
# "FLCL", 9
# "Witch Hunter Robin", 7
# ".hack//Sign", 7
# "Chobits", 7
# "Full Metal Panic!", 7
# "Mobile Suit Gundam Wing", 7
# "El Hazard: The Wanderers", 7
# "Mai-HiME", 6
# "Kimi ga Nozomu Eien", 6
$ ./resorter.R --input anime.txt --output new-ratings.txt --queries 10 --quantiles '0 0.33 0.9 1'
# Comparison commands: 1=yes, 2=tied, 3=second is better, p=print estimates, s=skip, q=quit
# Mean stderr: 70182  | Do you like 'RahXephon' better than 'Perfect Blue'? 2
# Mean stderr: 21607  | Do you like 'Monster' better than 'Death Note'? 1
# Mean stderr: 13106  | Do you like 'Kimi ga Nozomu Eien' better than 'Gunslinger Girl'? 3
# Mean stderr: 13324  | Do you like 'Kimi ga Nozomu Eien' better than 'Gankutsuou'? p
#                                           Media         Estimate              SE
#                                        Mai-HiME −2.059917500e+01 18026.307910587
#                             Kimi ga Nozomu Eien −2.059917500e+01 18026.308021536
#                              Witch Hunter Robin −1.884110950e-15     2.828427125
#                                     .hack//Sign −7.973125767e-16     2.000000000
#                                         Chobits  0.000000000e+00     0.000000000
#                               Full Metal Panic!  2.873961741e-15     2.000000000
#                         Mobile Suit Gundam Wing  5.846054261e-15     2.828427125
#                        El Hazard: The Wanderers  6.694628513e-15     3.464101615
#                                      Last Exile  1.911401531e+01 18026.308784841
#                             Fullmetal Alchemist  1.960906858e+01 18026.308743986
#                                 Gunslinger Girl  2.010412184e+01 18026.308672318
#                                            FLCL  2.059917511e+01 18026.308236990
#                                   Fruits Basket  2.059917511e+01 18026.308347939
#                                       RahXephon  2.059917511e+01 18026.308569837
#                                          Trigun  2.059917511e+01 18026.308458888
#                                         Jin-Rou  2.109422837e+01 18026.308740073
#                                      Death Note  2.109422837e+01 18026.308765943
#                                    Perfect Blue  2.109422837e+01 18026.308672318
#                         Serial Experiments Lain  2.158928163e+01 18026.308767629
#                                      Gankutsuou  2.208433490e+01 18026.308832127
#  Neon Genesis Evangelion: The End of Evangelion  2.257938816e+01 18026.308865814
#                                    Cowboy Bebop  2.307444143e+01 18026.308979636
#                                         Monster  2.307444143e+01 18026.308868687
# Mean stderr: 13324  | Do you like 'Monster' better than 'Jin-Rou'? s
# Mean stderr: 13324  | Do you like 'Last Exile' better than 'Death Note'? 3
# Mean stderr: 13362  | Do you like 'Mai-HiME' better than 'Serial Experiments Lain'? 3
# Mean stderr: 16653  | Do you like 'Trigun' better than 'Kimi ga Nozomu Eien'? 1
# Mean stderr: 14309  | Do you like 'Death Note' better than 'Kimi ga Nozomu Eien'? 1
# Mean stderr: 12644  | Do you like 'Trigun' better than 'Monster'? 3
$ cat new-ratings.txt
# "Media","Quantile"
# "Cowboy Bebop","3"
# "Monster","3"
# "Neon Genesis Evangelion: The End of Evangelion","3"
# "Death Note","2"
# "FLCL","2"
# "Fruits Basket","2"
# "Fullmetal Alchemist","2"
# "Gankutsuou","2"
# "Gunslinger Girl","2"
# "Jin-Rou","2"
# "Last Exile","2"
# "Perfect Blue","2"
# "RahXephon","2"
# "Serial Experiments Lain","2"
# "Trigun","2"
# "Chobits","1"
# "El Hazard: The Wanderers","1"
# "Full Metal Panic!","1"
# ".hack//Sign","1"
# "Kimi ga Nozomu Eien","1"
# "Mai-HiME","1"
# "Mobile Suit Gundam Wing","1"
# "Witch Hunter Robin","1"
~~~

# Source code

This R script requires the [BradleyTerry2](https://cran.r-project.org/web/packages/BradleyTerry2/index.html) & [argparser](https://bitbucket.org/djhshih/argparser) libraries to be available or installable.
([Andrew Quinn's Github version](https://github.com/hiAndrewQuinn/resorter) may be easier to install.)

<div class="admonition warning">
<div class="admonition-title">Dependency Compile Errors: install packages</div>
As with any user-installed language, you may run into compile errors while installing dependencies.

Look for a missing C library to install system-wide as root, or see if your package manager provides one of the dependencies already as a precompiled binary, so you can `apt-get install r-cran-bradleyterry2` or `apt-get install r-cran-lme4` to bypass any compile errors.
</div>

Save it as a script somewhere in your `$PATH` named `resorter`, and `chmod +x resorter` to make it executable.

~~~{.R}
#!/usr/bin/Rscript

# attempt to load a library implementing the Bradley-Terry model for inferring rankings based on
# comparisons; if it doesn't load, try to install it through R's in-language package management;
# otherwise, abort and warn the user
# https://www.jstatsoft.org/index.php/jss/article/download/v048i09/601
loaded <- library(BradleyTerry2, quietly=TRUE, logical.return=TRUE)
if (!loaded) { write("warning: R library 'BradleyTerry2' unavailable; attempting to install locally...", stderr())
              install.packages("BradleyTerry2")
              loadedAfterInstall <- library(BradleyTerry2, quietly=TRUE, logical.return=TRUE)
              if(!loadedAfterInstall) { write("error: 'BradleyTerry2' unavailable and cannot be installed. Aborting.", stderr()); quit() }
}
# similarly, but for the library to parse command line arguments:
loaded <- library(argparser, quietly=TRUE, logical.return=TRUE)
if (!loaded) { write("warning: R library 'argparser' unavailable; attempting to install locally...", stderr())
              install.packages("argparser")
              loadedAfterInstall <- library(argparser, quietly=TRUE, logical.return=TRUE)
              if(!loadedAfterInstall) { write("error: 'argparser' unavailable and cannot be installed. Aborting.", stderr()); quit() }
}
p <- arg_parser("sort a list using comparative rankings under the Bradley-Terry statistical model; see https://gwern.net/resorter", name="resorter")
p <- add_argument(p, "--input", short="-i",
                  "input file: a CSV file of items to sort: one per line, with up to two columns. (eg. both 'Akira\\n' and 'Akira, 10\\n' are valid).", type="character")
p <- add_argument(p, "--output", "output file: a file to write the final results to. Default: printing to stdout.")
p <- add_argument(p, "--verbose", "whether to print out intermediate statistics", flag=TRUE)
p <- add_argument(p, "--queries", short="-n", default=NA,
                  "Maximum number of questions to ask the user; defaults to N*log(N) comparisons. If already rated, 𝒪(n) is a good max, but the more items and more levels in the scale and more accuracy desired, the more comparisons are needed.")
p <- add_argument(p, "--levels", short="-l", default=5, "The highest level; rated items will be discretized into 1–l levels, so l=5 means items are bucketed into 5 levels: [1,2,3,4,5], etc. Maps onto quantiles; valid values: 2–100.")
p <- add_argument(p, "--quantiles", short="-q", "What fraction to allocate to each level; space-separated; overrides `--levels`. This allows making one level of ratings narrower (and more precise) than the others, at their expense; for example, one could make 3-star ratings rarer with quantiles like `--quantiles '0 0.25 0.8 1'`. Default: uniform distribution (1--5 → '0.0 0.2 0.4 0.6 0.8 1.0').")
p <- add_argument(p, "--no-scale", flag=TRUE, "Do not discretize/bucket the final estimated latent ratings into 1-l levels/ratings; print out inferred latent scores.")
p <- add_argument(p, "--progress", flag=TRUE, "Print out mean standard error of items")
argv <- parse_args(p)

# read in the data from either the specified file or stdin:
if(!is.na(argv$input)) { ranking <- read.csv(file=argv$input, stringsAsFactors=TRUE, header=FALSE); } else {
    ranking <- read.csv(file=file('stdin'), stringsAsFactors=TRUE, header=FALSE); }

# turns out noisy sorting is fairly doable in 𝒪(n * log(n)), so do that plus 1 to round up:
if (is.na(argv$queries)) { n <- nrow(ranking)
                           argv$queries <- round(n * log(n) + 1) }

# if user did not specify a second column of initial ratings, then put in a default of '1':
if(ncol(ranking)==1) { ranking$Rating <- 1; }
colnames(ranking) <- c("Media", "Rating")
# A set of ratings like 'foo,1\nbar,2' is not comparisons, though. We *could* throw out everything except the 'Media' column
# but we would like to accelerate the interactive querying process by exploiting the valuable data the user has given us.
# So we 'seed' the comparison dataset based on input data: higher rating means +1, lower means −1, same rating == tie (0.5 to both)
comparisons <- NULL
for (i in 1:(nrow(ranking)-1)) {
 rating1 <- as.numeric(ranking[i,]$Rating) ## HACK: crashes on reading its own output due to "?>? not meaningful for factors" if we do not coerce from factor to number?
 media1 <- ranking[i,]$Media
 rating2 <- as.numeric(ranking[i+1,]$Rating)
 media2 <- ranking[i+1,]$Media
 if (rating1 == rating2)
  {
     comparisons <- rbind(comparisons, data.frame("Media.1"=media1, "Media.2"=media2, "win1"=0.5, "win2"=0.5))
  } else { if (rating1 > rating2)
           {
            comparisons <- rbind(comparisons, data.frame("Media.1"=media1, "Media.2"=media2, "win1"=1, "win2"=0))
            } else {
              comparisons <- rbind(comparisons, data.frame("Media.1"=media1, "Media.2"=media2, "win1"=0, "win2"=1))
                   } } }
# the use of '0.5' is recommended by the BT2 paper, despite causing quasi-spurious warnings:
# > In several of the data examples (eg. `?CEMS`, `?springall`, `?sound.fields`), ties are handled by the crude but
# > simple device of adding half of a 'win' to the tally for each player involved; in each of the examples where this
# > has been done it is found that the result is similar, after a simple re-scaling, to the more sophisticated
# > analyses that have appeared in the literature. Note that this device when used with `BTm` typically gives rise to
# > warnings produced by the back-end glm function, about non-integer 'binomial' counts; such warnings are of no
# > consequence and can be safely ignored. It is likely that a future version of `BradleyTerry2` will have a more
# > general method for handling ties.
suppressWarnings(priorRankings <- BTm(cbind(win1, win2), Media.1, Media.2, data = comparisons))

if(argv$verbose) {
  print("higher=better:")
  print(summary(priorRankings))
  print(sort(BTabilities(priorRankings)[,1]))
}

set.seed(2015-09-10)
cat("Comparison commands: 1=yes, 2=tied, 3=second is better, p=print estimates, s=skip, q=quit\n")
for (i in 1:argv$queries) {

 # with the current data, calculate and extract the new estimates:
 suppressWarnings(updatedRankings <- BTm(cbind(win1, win2), Media.1, Media.2, br=TRUE, data = comparisons))
 coefficients <- BTabilities(updatedRankings)
 # sort by latent variable 'ability':
 coefficients <- coefficients[order(coefficients[,1]),]

 if(argv$verbose) { print(i); print(coefficients); }

 # select two media to compare: pick the media with the highest standard error and the media above or below it with the highest standard error:
 # which is a heuristic for the most informative pairwise comparison. BT2 appears to get caught in some sort of a fixed point with greedy selection,
 # so every few rounds pick a random starting point:
 media1N <- if (i %% 3 == 0) { which.max(coefficients[,2]) } else { sample.int(nrow(coefficients), 1) }
 media2N <- if (media1N == nrow(coefficients)) { nrow(coefficients)-1; } else { # if at the top & 1st place, must compare to 2nd place
   if (media1N == 1) { 2; } else { # if at the bottom/last place, must compare to 2nd-to-last
    # if neither at bottom nor top, then there are two choices, above & below, and we want the one with highest SE; if equal, arbitrarily choose the better:
    if ( (coefficients[,2][media1N+1]) > (coefficients[,2][media1N-1])  ) { media1N+1 } else { media1N-1 } } }

 targets <- row.names(coefficients)
 media1 <- targets[media1N]
 media2 <- targets[media2N]

 if (argv$`progress`) { cat(paste0("Mean stderr: ", round(mean(coefficients[,2]))), " | "); }
 cat(paste0("Is '", as.character(media1), "' greater than '", as.character(media2), "'? "))
 rating <- scan("stdin", character(), n=1, quiet=TRUE)

 switch(rating,
        "1" = { comparisons <- rbind(comparisons, data.frame("Media.1"=media1, "Media.2"=media2, "win1"=1, "win2"=0)) },
        "3" = { comparisons <- rbind(comparisons, data.frame("Media.1"=media1, "Media.2"=media2, "win1"=0, "win2"=1)) },
        "2" = { comparisons <- rbind(comparisons, data.frame("Media.1"=media1, "Media.2"=media2, "win1"=0.5, "win2"=0.5))},
        "p" = { estimates <- data.frame(Media=row.names(coefficients), Estimate=coefficients[,1], SE=coefficients[,2]);
                print(comparisons)
                print(warnings())
                print(summary(updatedRankings))
                print(estimates[order(estimates$Estimate),], row.names=FALSE) },
        "s" = {},
        "q" = { break; }
        )
}

# results of all the questioning:
if(argv$verbose) { print(comparisons); }

suppressWarnings(updatedRankings <- BTm(cbind(win1, win2), Media.1, Media.2, ~ Media, id = "Media", data = comparisons))
coefficients <- BTabilities(updatedRankings)
if(argv$verbose) { print(rownames(coefficients)[which.max(coefficients[2,])]);
                 print(summary(updatedRankings))
                 print(sort(coefficients[,1])) }

ranking2 <- as.data.frame(BTabilities(updatedRankings))
ranking2$Media <- rownames(ranking2)
rownames(ranking2) <- NULL

if(!(argv$`no_scale`)) {

    # if the user specified a bunch of buckets using `--quantiles`, parse it and use it,
    # otherwise, take `--levels` and make a uniform distribution
    levels <- max(2,min(100,argv$levels+1)) ## needs to be 2–100
    quantiles <- if (!is.na(argv$quantiles)) { (sapply(strsplit(argv$quantiles, " "), as.numeric))[,1]; } else {
      seq(0, 1, length.out=levels); }
    ranking2$Quantile <- with(ranking2, cut(ability,
                                    breaks=quantile(ability, probs=quantiles),
                                    labels=1:(length(quantiles)-1),
                                    include.lowest=TRUE))
    df <- subset(ranking2[order(ranking2$Quantile, decreasing=TRUE),], select=c("Media", "Quantile"));
    if (!is.na(argv$output)) { write.csv(df, file=argv$output, row.names=FALSE) } else { print(df); }
} else { # return just the latent continuous scores:
         df <- data.frame(Media=rownames(coefficients), Estimate=coefficients[,1]);
         if (!is.na(argv$output)) { write.csv(df[order(df$Estimate, decreasing=TRUE),], file=argv$output, row.names=FALSE); } else {
             print(finalReport); }
       }

cat("\nResorting complete")
~~~

# Background

## Rating Inflation

In rating hundreds of media on a review site like [GoodReads](!W), Amazon, [MyAnimeList](https://myanimelist.net/), [Uber/Lyft](https://www.youtube.com/watch?v=iu6eWy7BKKI "'Service quality in the gig economy', Athey et al 2018"), [freelancing markets](/doc/statistics/order/comparison/2022-filippas.pdf "'Reputation Inflation', Filippas et al 2018") etc, the distributions tend to become 'lumpy' and concentrate on the top few possible ratings: if it's a 10-point scale, you won't see many below 7, usually, or if it's 5-stars [then anything](https://xkcd.com/325/) [below 4-stars indicates profound hatred](https://xkcd.com/1098/), leading to a J-shaped distribution and the Internet's version of [grade inflation](!W).
After enough time and inflation, the ratings have degenerated into a noninformative binary rating scale, and some sites, recognizing this, abandon the pretense, like [YouTube](https://blog.youtube/news-and-events/five-stars-dominate-ratings/ "Five Stars Dominate Ratings") or [Netflix switching from 5-stars to like/dislike](https://variety.com/2017/digital/news/netflix-thumbs-vs-stars-1202010492/ "Netflix Replacing Star Ratings With Thumbs Ups and Thumbs Downs").
The self-selection and other issues in existing ratings like [publication bias](https://datacolada.org/72 "Metacritic Has A (File-Drawer) Problem") have some perverse consequences: for example, winning an award can *lower* a book's GoodReads average rating, because the award leads a wider, less receptive, audience to read the book ([Kovács & Sharkey 2014](/doc/culture/2014-kovacs.pdf "The Paradox of Publicity: How Awards Can Negatively Affect the Evaluation of Quality")).

This is unfortunate if you want to provide ratings & reviews to other people and indicate your true preferences; when I like on [MALgraph](https://anime.plus/gwern/ratings,anime) and see that over half my anime ratings are in the range 8--10, then, my ratings having degenerated into a roughly 1--3 scale (crap/good/great) makes it harder to see which ones are truly worth watching & also which ones I might want to go back and rewatch.
So the ratings carry much less information than one might have guessed from the scale (a 10-point scale has 3.32 bits of information in each rating, but if it's de facto degenerated into a 3-point scale, then the information has halved to 1.58 bits).
If instead, my ratings were uniformly distributed over the 1--10 scale, such that 10% were rated 1, 10% were rated 2, etc, then my ratings would be much more informative, and my opinion clearer.
(First-world problems, perhaps, but still annoying.)

## What Distribution *Should* Ratings Be?

If the J-shaped distribution is no good, what distribution ought one's ratings to be?

A normal distribution has a certain esthetic appeal, and common, but that's no justification.
First, there's not much reason to think that media ought to be normally-distributed in the first place.
The universality of the normal distribution comes from the [CLT](!W "Central limit theorem"), and how many variables being added will tend to yield a normal; however, are works of art only the *sum of their parts*?
I would say no: they are something more like the multiple of their parts, and multiplying out many random variables tends to give something like a [log-normal distribution](!W) instead.
If art were really normally distributed, why do we so often watch an anime and say, "that had really great art and music and voice-acting but... the plot was *so* stupid I couldn't enjoy it at all and I have to give it a low rating and will never watch it again"? After all, if they only summed, all the other variables would be more than good enough to make the overall score great too. Meanwhile, a work which does well on all aspects may achieve greatness simply through lacking any flaws---it all comes together in more than the sum of its parts.
Second, we are not watching random samples drawn from the overall distribution, we are generally trying to draw a highly biased sample from the right-tail of quality (ie. watch only good ones).
Our sample of ratings would, if we are doing a good job, look nothing like the overall distribution, in much the same way that a graph of heights in the NBA would look nothing like a graph of heights in the US population.

A uniform distribution has similar problem.
Its advantage, mentioned above, is that it contains more information: a normal distribution clumps ratings towards the middle with most falling in 5, with only a few reaching 1 or 10, while a uniform distribution maximizes the information---the worst 10% get rated 1, and so on to the best 10% getting rated 10.
If you learn something is a 5 from a uniform distribution, you learn a lot more (it's in the 50--60% range) than if it were a normal distribution (it's 50±??%).

But, I think I would rather look at a critic's ratings if they used a normal distribution instead of a uniform distribution.
Why? Because, as I said, we usually try to watch *good* stuff, and if I see something rated a 10, I know it's in the top percentile or two, while the uniform would be 5--10× less selective and a 10 there only tells me that it's somewhere in the top decile, which is not too selective.
If a critic thought something was in the top percentile, I will pay attention; but top decile is not too useful in helping me find things I may want.

So, I think our target distribution ought to maximize *usefulness*: it is just a summary of an unknowable underlying distribution, which we summarize pragmatically as ratings, and so [statistics like ratings](/research-criticism "'How Should We Critique Research?', Gwern 2019") can only be right or wrong as defined by their intended use.
On a rating website, we are not interested in making fine distinctions among mediocre or trash.
We are looking for interesting new candidates to consider, we are looking for the best.
A skew maximizes the provided information to the reader in the region of interest of likely recommendations.
So our distribution ought to throw most of our ratings into an uninformative 'meh' bucket, and spend more time on the right-tail extreme: do we think a given work an all-time masterpiece, or exceptional, or merely good?

What we want is a *reverse J-shaped distribution*: one in which most ratings are the lowest, and only a few are the highest.
(For smaller sets of ratings, a less extreme skew would be useful: it's no good if most of the ratings are almost empty. One might also struggle to, even using pairwise ratings, express such precise percentiles and fall back to a minimum size of, say, 5%.)

In terms of percentiles, with my ~458 anime watched/dropped, I might bucket it like this:

<div class="columns">
#. 0--50% (_n_ = 231)
#. 51--75% (_n_ = 112)
#. 76%--89% (_n_ = 62)
#. 90--93% (_n_ = 16)
#. 94--95% (_n_ = 11)
#. 96% (_n_ = 7)
#. 97% (_n_ = 6)
#. 98% (_n_ = 6)
#. 99% (_n_ = 5)
#. \>99.5% (_n_ = 2)
</div>

That would correspond to using the option `--quantiles '0 0.5 0.75 0.89 0.93 0.95 0.96 0.97 0.98 0.99 0.995'`.

## Rescaling

### Interactive Ranking Through Sorting

For only a few ratings like 10 or 20, it's easy to manually review and rescale ratings and resolve the ambiguities (which '8' is worse than the other '8's and should be knocked down to 7?), but past that, it starts to become tedious and because judgment is so fragile and subjective and ['choice fatigue'](!W "Decision fatigue") begins to set in, I find myself having to repeatedly scan the list and ask myself "is X *really* better than Y...? hm...".
So unsurprisingly, for a large corpus like my 408 anime or 2059 books, I've never bothered to try to do this---much less do it occasionally as the ratings drift.

If I had some sort of program which could query me repeatedly for new ratings, store the results, and then spit out a consolidated list of exactly how to change ratings, then I might be able to, once in a great while, correct my ratings.
This would help us re-rate our existing media corpuses, but it could also help us sort other things: for example, we could try to prioritize future books or movies by taking all the ones we marked 'to read' and then doing comparisons to rank each item by how excited we are about it or how important it is or how much we want to read it soon.
(If we have way too many things to do, we could also sort our overall To-Do lists this way, but probably it's easy to sort them by hand.)

But it can't ask me for absolute ratings, because if I was able to easily give uniformly-distributed ratings, I wouldn't have this problem in the first place!
So instead it should calculate rankings, and then take the final ranking and distribute them across however many buckets there are in the scale: if I rate 100 anime for MAL's 1--10 ranking, then it will put the bottom 10 in the '1' bucket, the 10--20^th^ into the '2' bucket, etc
This cannot be done automatically.

How to get rankings: if there are 1,000 media, it's impossible for me to explicitly rank a book '#952', or '#501'. Nobody has that firm a grip.
Perhaps it would be better for it to ask me to compare pairs of media?
Comparison is much more natural, less fatiguing, and helps my judgment by reminding me of what other media there are and how I think of them---when a terrible movie gets mentioned in the same breath as a great movie, it reminds you why one was terrible and the other great.
Comparison also immediately suggests an implementation as the classic comparison sort algorithms like Quicksort or Mergesort, where the comparison argument is an IO function which simply calls out to the user; yielding a reasonable 𝒪(n · log(_n_)) number of queries (and possibly much less, 𝒪(_n_), if we have the pre-existing ratings and can treat it as an [adaptive sort](!W)).
So we could solve this with a simple script in any decent programming language like Python, and this sort of re-sorting is provided by websites such as [Flickchart](https://www.flickchart.com/Splash.aspx?return=%2f).

### Noisy Sorting

The comparison-sort algorithms make an assumption that is outrageously unrealistic in this context: they assume that the comparison is 100% accurate.

That is, say, you have two sorted lists of 1,000 elements each and you compare the lowest element of one with the highest element of the other and the first is higher, then all 1,000 items in the first are higher than all 1,000 items in the second, that of the (<span class="subsup"><sub>2</sub><sup>1,000</sup></span>) = 499,500 possible pairwise comparisons, the sorting algorithms assume that not a single item is out of place, not a single pairwise comparison would be incorrect.
This assumption is fine in programming, since the CPU is good at comparing bits for equality & may go trillions of operations without making a single mistake; but it's absurd to expect this level of reliability of a human for any task, much less one in which we are clumsily feeling for the invisible movements of our souls in response to great artists.

Our comparisons of movies, or books, or music, *are* error-prone and so we need some sort of statistical sorting algorithm.
How much does this hurt? Do we get some much worse sample-efficiency?

No.
It turns out that the "noisy sorting" setting is not that different from the comparison sort setting: the optimal asymptotic performance there too is 𝒪(_n_ · log(_n_)).
The penalty from the comparison error rate _p_ just gets folded into the constants (since as _p_ approaches 0, it gets easier and turns into regular comparison sort).

Some references:

- Slater 1961, ["Inconsistencies in a schedule of paired comparisons"](/doc/statistics/order/comparison/1961-slater.pdf)
- David 1963, ["The method of paired comparisons"](https://apps.dtic.mil/sti/pdfs/ADA417190.pdf#page=15)
- Adler et al 1994, ["Selection in the presence of noise: The design of playoff systems"](http://www-cgi.cs.cmu.edu/afs/cs.cmu.edu/Web/People/harchol/Papers/SODA94-ranking.pdf)
- Feige et al 1994, ["Computing with noisy information"](https://cadmo.ethz.ch/education/lectures/HS18/SAADS/papers/computing_noisy_information.pdf)
- Glickman 1999, ["Parameter estimation in large dynamic paired comparison experiments"](https://math.bu.edu/individual/mg/research/glicko.pdf)
- Pelc 2002, ["Searching games with errors---fifty years of coping with liars"](/doc/statistics/order/comparison/2002-pelc.pdf)
- Chu & Ghahramani 2005, ["Preference learning with Gaussian processes"](https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.437.20&rep=rep1&type=pdf)
- Karp & Kleinberg 2007, ["Noisy binary search and its application"](/doc/statistics/order/comparison/2007-karp.pdf "‘Noisy binary search and its applications’, Karp & Kleinberg 2007")
- Radlinski & Joachims 2007, ["Active exploration for learning rankings from clickthrough data"](https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.210.2439&rep=rep1&type=pdf)
- Kenyon-Mathieu & Schudy 2007, ["How to rank with few errors"](https://cs.brown.edu/research/pubs/theses/masters/2007/schudy.pdf)
- Ailon et al 2008, ["Aggregating inconsistent information: ranking and clustering"](/doc/statistics/order/comparison/2008-ailon.pdf "'Aggregating inconsistent information: Ranking and clustering', Ailon et al 2008")
- Braverman & Mossel 2008, ["Noisy sorting without resampling"](https://arxiv.org/abs/0707.1051 "'Noisy Sorting Without Resampling', Braverman & Mossel 2007") / Braverman & Mossel 2009, ["Sorting from noisy information"](https://arxiv.org/abs/0910.1191 "'Sorting from Noisy Information', Braverman & Mossel 2009")
- Yue & Joachims 2011, ["Beat the mean bandit"](http://www.yisongyue.com/publications/icml2011_beat_the_mean.pdf)
- Houlsby et al 2011, ["Bayesian Active Learning for Classification and Preference Learning"](https://arxiv.org/abs/1112.5745)
- Yue et al 2012, ["The _K_-armed dueling bandits problem"](https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.165.1421&rep=rep1&type=pdf)
- Busa-Fekete et al 2014, ["Preference-based rank elicitation using statistical models: The case of Mallows"](https://inria.hal.science/hal-01079369/document)
- Szorenyi et al 2015, ["Online Rank Elicitation for Plackett-Luce: A Dueling Bandits Approach"](https://proceedings.neurips.cc/paper/2015/file/7eacb532570ff6858afd2723755ff790-Paper.pdf)
- Maystre & Grossglauser 2015, ["Just Sort It! A Simple and Effective Approach to Active Preference Learning"](https://arxiv.org/abs/1502.05556)
- Christiano et al 2017, ["Deep reinforcement learning from human preferences"](https://arxiv.org/abs/1706.03741#openai); Henderson et al 2017, ["OptionGAN: Learning Joint Reward-Policy Options using Generative Adversarial Inverse Reinforcement Learning"](https://arxiv.org/abs/1709.06683)
- Le et al 2017, ["Analogical-based Bayesian Optimization"](https://arxiv.org/abs/1709.06390)
- Chen et al 2017, ["Spectral Method and Regularized MLE Are Both Optimal for Top-_K_ Ranking"](https://arxiv.org/abs/1707.09971 "'Spectral Method and Regularized MLE Are Both Optimal for Top-<em>K</em> Ranking', Chen et al 2017")
- Kazemi et al 2018, ["Comparison Based Learning from Weak Oracles"](https://arxiv.org/abs/1802.06942)
- Liu et al 2018, ["Model-based learning from preference data"](https://hal.science/hal-01972948/document#pdf)

## Implementation

So we'd like a command-line tool which consumes a list of pairs of media & ratings, then queries the user repeatedly with pairs of media to get the user's rating of which one is better, somehow modeling underlying scores while allowing for the user to be wrong in multiple comparisons and ideally picking whatever is the 'most informative' next pair to ask about to converge on accurate rankings as quickly as possible, and after enough questions, do a final inference of the full ranking of media and mapping it onto a uniform distribution over a particular rating scale.

The natural way to see the problem is to treat every competitor as having an unobserved [latent variable](!W) 'quality' or 'ability' or 'skill' on a cardinal scale which is measured with error by comparisons, and then weaken transitivity to chain our comparisons: if A beats B and B beats C, then *probably* A beats C, weighted by how many times we've observed beating and have much precise our estimate of A-C's latent variables are.

Paired or comparison-based data comes up a lot in competitive contexts, such as the famous [Elo rating system](!W) or the Bayesian [TrueSkill](!W).
A general model for dealing with it is the [Bradley-Terry model](!W).

There are at least two packages in R for dealing with Bradley-Terry models, [`BradleyTerry2`](https://www.jstatsoft.org/index.php/jss/article/download/v048i09/601 "Bradley-Terry Models in R: The BradleyTerry2 Package") and [`prefmod`](https://www.jstatsoft.org/index.php/jss/article/download/v048i10/602 "prefmod: An R Package for Modeling Preferences Based on Paired Comparisons, Rankings, or Ratings").
The latter supports more sophisticated analyses than the former, but it wants its data in an inconvenient format, while `BradleyTerry2` is more easily incrementally updated.
(I want to supply my data to the library as a long list of triplets of media/media/rating, which is then easily updated with user-input by simply adding another triplet to the bottom; but `prefmod` wants a column for each possible media, which is awkward to start with and gets worse if there are 1,000+ media to compare.)

We start with two vectors: the list of media, and the list of original ratings.
The original ratings, while lumpy and in need of improving, are still useful information which should not be ignored; if BT-2 were a Bayesian library, we could use them as informative priors, but it's not, so instead I adopt a hack in which the program runs through the list, comparing each anime with the next anime, and if equal, it's treated as a tie, and otherwise they are recorded as a win/loss---so even from the start we've made a lot of progress towards inferring their latent scores.

Then a loop asks the user _n_ comparisons; we want to ask about the media whose estimates are most uncertain, and a way of estimating that is looking at which media have the biggest [standard error](!W).
You might think that asking about only the two media with the current biggest standard error would be the best exploration strategy (since this corresponds to reinforcement learning and multi-armed bandit approaches where you start off by exploring the most uncertain things), but surprisingly, this leads to asking about the same media again and again, even as the standard error plummets.
I'm not sure why this happens, but I think it has to do with the prior information creating an ordering or hierarchy on all the media, and then the maximum-likelihood estimating leads to repeating the same question again and again to shift the ordering up or down the cardinal scale (even our discretized ratings will be invariant no matter how the estimates are translated up and down).
So instead, we alternate between asking about the media with the largest standard error (choosing the nearest neighbor, up or down, with the larger standard error), and occasionally picking at random, so it usually focuses on the most uncertain ones but will occasionally ask about other media as well.
(Somewhat analogous to fixed-epsilon exploration in RL.)

After all the questions are asked, a final estimation is done, the media are sorted by rank, and mapped back onto the user-specified rating scale.

### Why Not Bayes?
#### Bayesian Improvements

There are two problems with this approach:

#. it does not come with any principled indication of uncertainty,
#. and as a consequence, it may not be asking the optimal questions.

The first is the biggest problem because we have no way of knowing when to stop.
Perhaps after 10 questions, the *real* uncertainty is still high and our final ratings will still be missorted; or perhaps diminishing returns had set in and it would have taken so many more questions to stamp out the error that we would prefer just to correct the few erroneous ratings manually in an once-over.
And we don't want to crank up the question-count to something burdensome like 200 just on the off-chance that the sorting is insufficient.
Instead, we'd like some comprehensible probability that each media is assigned to its correct bucket, and perhaps a bound on overall error: for example, I would be satisfied if I could specify something like '90% probability that all media are at least in their correct bucket'.^[I think this could be done by sampling the posterior: draw a random sample of the estimated score from the posterior for each media and discretize them all down; do this, say, 100 times; compare the 100 discretized and see how often any media changes categories. If every media is in the same bucket, say, in 95 of those samples---_The Godfather_ is in the 5-star bucket in 95 of the 100 samples and in the 4-star bucket in the other 5---then the remaining uncertainty in the estimated scores must be small.]

Since BF-2 is fundamentally a frequentist library, it will never give us this kind of answer; all it has to offer in this vein are _p_-values---which are answers to questions I've never asked---and standard errors, which are *sort* of indicators of uncertainty & better than nothing but still imperfect.
Between our interest in a sequential trial approach and our interest in producing meaningful probabilities of errors (and my own preference for Bayesian approaches in general), this motivates looking at Bayesian implementations.

The Bradley-Terry model can be fit easily in JAGS/Stan; two less and more elaborate examples are in [Jim Albert's implementation](https://web.archive.org/web/20160102165131/http://bayes.bgsu.edu/webinar.11.2012/R%20output/Rcode.part4.html "Part 4: Introduction to JAGS") & [Shawn E. Hallinan](/doc/statistics/order/comparison/2005-hallinan.pdf "Paired Comparison Models for Ranking National Soccer Teams"), and [`btstan`](https://github.com/nxskok/btstan/blob/master/R/btstan.R) respectively.
Although it doesn't implement the extended B-T with ties, Albert's example is easily adapted, and we could try to infer rankings like thus:

~~~{.R}
comparisons2 <- comparisons[!(comparisons$win1==0.5),]

teamH = as.numeric(comparisons2$Media.1)
teamA = as.numeric(comparisons2$Media.2)
y = comparisons2$win1
n = comparisons2$win1 + comparisons2$win2
N = length(y)
J = length(levels(comparisons$Media.1))
data = list(y = y, n = n, N = N, J = J, teamA = teamA, teamH = teamH)
data ## reusing the baseball data for this example:
# $y
#  [1] 4 4 4 6 4 6 3 4 4 6 6 4 2 4 2 4 4 6 3 5 2 4 4 6 5 2 3 4 5 6 2 3 3 4 4 2 2 1 1 2 1 3
#
# $n
#  [1] 7 6 7 7 6 6 6 6 7 6 7 7 7 7 6 7 6 6 6 6 7 7 6 7 6 7 6 6 7 6 7 6 7 7 6 6 7 6 7 6 7 7
#
# $N
# [1] 42
#
# $J
# [1] 7
#
# $teamA
#  [1] 4 7 6 2 3 1 5 7 6 2 3 1 5 4 6 2 3 1 5 4 7 2 3 1 5 4 7 6 3 1 5 4 7 6 2 1 5 4 7 6 2 3
#
# $teamH
#  [1] 5 5 5 5 5 5 4 4 4 4 4 4 7 7 7 7 7 7 6 6 6 6 6 6 2 2 2 2 2 2 3 3 3 3 3 3 1 1 1 1 1 1

model1 <- "model {
    for (i in 1:N){
        logit(p[i]) <- a[teamH[i]] - a[teamA[i]]
        y[i] ~ dbin (p[i], n[i])
    }
    for (j in 1:J){
        a[j] ~ dnorm(0, tau)
    }
    tau <- pow(sigma, -2)
    sigma ~ dunif (0, 100)
}"
library(runjags)
j1 <- autorun.jags(model=model1, monitor=c("a", "y"), data=data); j1
~~~

(This reuses the converting-priors-to-data trick from before.)
This yields sensible ratings but MCMC unavoidably have overhead compared to a quick iterative maximum-likelihood algorithm which only estimates the parameters---it takes about 1s to run on the example data.
Much of that overhead is from JAGS's setup & interpreting the model, and could probably be halved maybe by using Stan instead (since it caches compiled models) but regardless, 0.5s is too long for particularly pleasant interactive use (total time from response to next question should be <0.1s for best UX) but it's worth paying if we can get much better questions?
There might be speedups available; this is about estimating latent normal/Gaussian variables, which frequently has fast implementations.
For example, it would not surprise me if it turned out that the Bayesian inference could be done outside of MCMC through an analytic solution, or more likely, a Laplacian approximation, such as implemented in [INLA](https://www.r-inla.org/) which supports [latent Gaussians](/doc/statistics/order/comparison/2010-martino.pdf "'Case Studies in Bayesian Computation using INLA', Martino & Rue 2010").
More recently, Stan supports [gradient descent](!W) optimization-based Bayesian inference ([variational inference](!W)), which deliver accurate enough posteriors while being fast enough for interactive use.

#### Optimal Exploration

So moving on, with a MCMC implementation, we can look at how to optimally sample data.
In this case, since we're collecting data and the user can stop anytime they feel like, we aren't interesting in loss functions so much as maximizing information gain---figuring out which pair of media yields the highest "expected information gain".

One possible approach would be to repeat our heuristic: estimate the entropy of each media, pick the one with the highest entropy/widest posterior distribution, and pick a random comparison.
A better one might be to vary this: pick the two media who most overlap (more straightforward with posterior samples of the latent variables than with just confidence intervals, since confidence intervals, after all, do not mean "the true variable is in this range with 95% probability").
That seems much better but still probably not optimal, as it ignores any downstream effects---we might reduce uncertainty more by sampling in the middle of a big cluster of movies rather than sampling two outliers near each other.

Formal EI is not too well documented at an implementation level, but the most general form of the algorithm seems to go: for each possible action (in this case, each possible pair of media), draw a sample from the posterior as a hypothetical action (from the MCMC object, draw a score estimate for both media and compare which is higher), rerun & update the analysis (add the result of the comparison to the dataset & run the MCMC again on it to yield a new MCMC object), and on these two old and new MCMC objects, calculate the entropy of the distributions (in this case, the sum of all the logs of probability of the higher in each possible pair of media being higher?), and subtract new from old; do that ~10 times for each so the estimated change in entropy is reasonably stable; then find the possible action with the largest change in entropy, and execute that.

##### Computational Requirement

Without implementing it, this is infeasible.
From a computational perspective: there are (<span class="subsup"><sub>2</sub><sup><em>media</em></sup></span>) possible actions; each MCMC run takes ~1s; there must be 10 MCMC runs; and the entropy calculations require a bit of time.
With just 20 media, that'd require ((<span class="subsup"><sub>2</sub><sup>20</sup></span>) × 10 × 1) / 60 = (190 × 10) / 60 = 31 minutes.

We could run these in parallel^[We could also speculatively execute while waiting for the user to make the current rating, as there are only 3 possible choices (better/worse/tie) and we have to compute 1 of them eventually anyway; if we compute the optimal next choice for all 3 hypothetical choices so we already know what next to ask, then as far as the user is concerned, it may appear instantaneous with zero latency.], could try to cut down the MCMC iterations even more and risk the occasional non-convergence, could try calculating EI for only a limited number of choices (perhaps 20 randomly chosen options), or look for some closed-form analytic solution (perhaps assuming normal distributions?)---but it's hard to see how to get total runtime down to 0.5s---much less ~0.1s.
And on the packaging side of things, requiring users to have JAGS (much less Stan) installed at all makes `resorter` harder to install and much more likely that there will be opaque runtime errors.

If asking the user to compare two things was rare and expensive data, if we absolutely had to maximize the informational value of every single question, if we were doing hardcore science like [astronomical observations](https://hosting.astro.cornell.edu/~loredo/bayes/bae.pdf "'Bayesian Adaptive Exploration', Loredo & Chernoff 2003") where every minute of telescope time might be measured in thousands of dollars, then a runtime of 1 hour to optimize question choice would be fine. But we're not.
If the user needs to be asked 5 additional questions because the standard-error exploration heuristic is suboptimal, that costs them a couple seconds. Not a big deal.
And if we're not exploiting the additional power of Bayesian methods, why bother switching from BF-2 to JAGS?

# See Also

- [Preference learning with GPT-2](/gpt-2-preference-learning "'GPT-2 Preference Learning for Music Generation', Gwern 2019"){.backlink-not}

# External Links

- [Utility Function Extractor: Simple comparison polling to create utility functions](https://forum.effectivealtruism.org/posts/9hQFfmbEiAoodstDA/simple-comparison-polling-to-create-utility-functions)
- ["fullrank: An interactive CLI tool and Python library for Bayesian inference of list rankings based on noisy comparisons."](https://github.com/max-niederman/fullrank "‘<code>fullrank</code>: An interactive CLI tool and Python library for Bayesian inference of list rankings based on noisy comparisons’, Niederman 2025") ([blog](https://www.lesswrong.com/posts/ojZL2iSgFnASmRNnN/fullrank-bayesian-noisy-sorting-1 "‘Fullrank: Bayesian Noisy Sorting’, Niederman 2025"))
