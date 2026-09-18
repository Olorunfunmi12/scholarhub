**Subject:** Nontidal data does help predict the tidal *Enterococcus*

---

Hi Professor [name],

Thanks so much for the note — really glad the first set of results was useful! I went
ahead and dug into your question about the nontidal data, and it turns out it *does* add
real predictive value for the tidal *Enterococcus*.

The short version: I took the harbor model we already had and folded in the upstream
conditions from Gwynns Falls and Jones Falls, matching each harbor sample to the stream
readings from the same week. Once the upstream data goes in, the model gets noticeably
better — the R² climbs from about 0.17 to 0.28, and the ability to flag exceedances
(>104 MPN/100 mL) improves from 0.75 to 0.80 AUC. It holds up across different models and
random seeds and is statistically significant, so I'm confident it's a real effect and
not noise.

What I found most interesting is *what's* driving it: the biggest signal is simply the
streams' own *Enterococcus*, Jones Falls especially. When the streams are clean, only
about 1% of harbor samples exceed the standard; when the streams run high, that jumps to
nearly 40%. It really does look like the streams are carrying the bacterial load down into
the harbor.

Two quick notes for when we write it up. First, the upstream data *alone* predicts almost
as well as the harbor's own chemistry, which could be handy for a real-time warning tool.
Second, since stream bacteria are so rain-driven, I'd like to add the rainfall term to the
baseline to cleanly separate the "streams carrying load" effect from the shared weather
signal — I can run that as soon as we pull in the NOAA record, and the streamflow piece is
ready to go the moment the daily discharge data comes through.

I've put the full notebook, the figures, and a draft of the section here: **[link]**.
Happy to walk through any of it, or talk it over whenever suits you.

Best,
Olorunfunmi
