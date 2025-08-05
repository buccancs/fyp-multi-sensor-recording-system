# Introduction: Importance of Emotion Analysis in Research and Applications

Emotion analysis plays a **fundamental role across many different
fields**, serving as a core methodology to tackle diverse research
questions. For example, **healthcare and psychology** use emotion
detection to help diagnose and treat mental health disorders (by
monitoring stress, anxiety, depression
indicators)[\[1\]](https://www.mdpi.com/1424-8220/24/11/3484#:~:text=Emotion%20detection%20is%20a%20research,to%20transform%20various%20industries%20and).
In **education**, sensing students' emotional states can enable
personalized learning experiences, as detecting frustration or
engagement helps tailor teaching
methods[\[1\]](https://www.mdpi.com/1424-8220/24/11/3484#:~:text=Emotion%20detection%20is%20a%20research,to%20transform%20various%20industries%20and).
In the **entertainment and gaming industry**, emotion recognition is
used to enhance user experiences (e.g. games adapting to player
emotions)[\[2\]](https://www.mdpi.com/1424-8220/24/11/3484#:~:text=Accurate%20detection%20of%20emotions%20can,Thus%2C%20the%20significance%20of).
**Customer experience and marketing** research also relies on emotion
analysis -- for instance, measuring consumers' emotional responses (via
facial expressions, heart rate, or galvanic skin response) provides
insight into product appeal and customer
satisfaction[\[2\]](https://www.mdpi.com/1424-8220/24/11/3484#:~:text=Accurate%20detection%20of%20emotions%20can,Thus%2C%20the%20significance%20of).
Even in **public safety and security**, emotion and stress detection
have value: systems that monitor for signs of fear, agitation or stress
in crowds can help identify suspicious behavior or prevent
incidents[\[3\]](https://www.mdpi.com/1424-8220/24/11/3484#:~:text=disorders%2C%20facilitate%20personalized%20learning%2C%20and,Thus%2C%20the%20significance%20of).
These examples -- spanning mental health, education, entertainment,
marketing, and security -- underscore that the **ability to
automatically analyze human emotions is broadly important**. In each
case, emotion analysis offers an objective window into internal states,
which can greatly *"transform various industries and improve quality of
life"* when applied
appropriately[\[4\]](https://www.mdpi.com/1424-8220/24/11/3484#:~:text=gaming%20and%20virtual%20reality,to%20transform%20various%20industries%20and).

## Why Measure Emotions *Contactlessly*?

Given the importance of emotion and stress data, a key question is **how
to measure these signals in a practical, non-intrusive way**.
Traditional methods often involve contact sensors or even bio-sampling
(e.g. drawing blood to check stress hormones), which can be inconvenient
or distressing for participants. **Contactless measurement** of
emotional or physiological signals offers several advantages. *Firstly*,
it is **less intrusive and more comfortable** for individuals being
monitored[\[5\]](https://www.frontiersin.org/journals/communications-and-networks/articles/10.3389/frcmn.2021.636293/full#:~:text=RPM%20sensors%20can%20be%20broadly,video%2C%20sound%2C%20radar%2C%20and%20other).
For example, wearable sensors attached to the skin can be obtrusive or
cause discomfort over long periods, especially for the elderly, infants,
or patients; by contrast, camera-based or other remote sensing methods
require no physical contact and thus minimize
burden[\[5\]](https://www.frontiersin.org/journals/communications-and-networks/articles/10.3389/frcmn.2021.636293/full#:~:text=RPM%20sensors%20can%20be%20broadly,video%2C%20sound%2C%20radar%2C%20and%20other).
This comfort factor is critical in sensitive populations -- consider
neonates in intensive care, where adhesive electrodes for heart rate or
stress monitoring can **damage fragile skin and cause pain**. In such
cases, a video camera that measures vital signs optically avoids further
harming the
infant[\[6\]](https://colab.ws/articles/10.1049%2Fhtl.2014.0077#:~:text=Current%20technologies%20to%20allow%20continuous,The).
*Secondly*, contactless methods improve hygiene and safety. Because no
direct contact is needed, the risk of **infection or
cross-contamination** is reduced -- an important benefit underscored
during scenarios like the COVID-19
pandemic[\[7\]](https://www.frontiersin.org/journals/communications-and-networks/articles/10.3389/frcmn.2021.636293/full#:~:text=certain%20advantages%20over%20them,video%2C%20sound%2C%20radar%2C%20and%20other).
*Thirdly*, **remote sensing allows monitoring in situations where
attaching sensors is impractical**, such as in driving or workplace
settings, or when one needs to measure multiple people simultaneously
(e.g. assessing a classroom's engagement via camera). In sum,
**contactless emotion/stress measurement provides a convenient, safe,
and scalable approach** to gathering physiological data, enabling
continuous monitoring without disrupting the subject's natural behavior.
研究ers have begun capitalizing on these benefits; for instance, recent
systems use standard cameras to remotely track heart rate and stress,
achieving accuracy comparable to contact sensors while subjects go about
normal
activities[\[5\]](https://www.frontiersin.org/journals/communications-and-networks/articles/10.3389/frcmn.2021.636293/full#:~:text=RPM%20sensors%20can%20be%20broadly,video%2C%20sound%2C%20radar%2C%20and%20other).

*(Note: In this report, we focus specifically on* *stress* *as a target
emotional state, examining how it can be defined and measured via both
contact-based and contactless methods.)*

## Defining Stress: Scientific vs. Colloquial Meaning

Before exploring measurements, it is important to clarify **what
"stress" means** in a scientific context, and how this differs from
everyday usage. In psychology and physiology, **stress is typically
defined as the body's physical and mental response to demands or
challenges (stressors)**. For example, the U.S. National Institute of
Mental Health defines stress as *"the physical or mental response to an
external cause"*
(stressor)[\[8\]](https://www.nimh.nih.gov/health/publications/so-stressed-out-fact-sheet#:~:text=What%20is%20stress%3F%20Stress%20is,repeatedly%20over%20a%20long%20time).
This response involves a cascade of neurological and hormonal changes --
popularly known as the "fight-or-flight" response -- preparing the
organism to cope with the threat or
demand[\[9\]](https://www.psychologytoday.com/us/basics/stress#:~:text=Reviewed%20by%20Psychology%20Today%20Staff).
Crucially, **this formal definition encompasses both negative and
positive forms of stress**. Stress isn't inherently bad -- in fact,
moderate stress can be motivating or adaptive. Official sources note
that *"stress can be positive or negative. For example, it may inspire
you to meet a deadline, or it may cause you to lose
sleep."*[\[10\]](https://www.nimh.nih.gov/health/publications/so-stressed-out-fact-sheet#:~:text=,cause%20you%20to%20lose%20sleep).
In other words, scientifically, *stress is a neutral term* describing a
state of heightened arousal and resource mobilization, which can occur
in many contexts (eustress vs. distress).

By contrast, in **everyday language** "stress" usually refers to a
subjective feeling of **strain, pressure, or being overwhelmed**, almost
always with a negative connotation. People say "I'm stressed out" to
mean they feel anxious or overburdened. This colloquial usage tends to
blur the distinction between the external trigger and the internal
response -- and it ignores the possibility of positive stress. The
scientific view separates the **stressor** (e.g. an exam, a work
deadline) from the **stress response** (the body's
reaction)[\[8\]](https://www.nimh.nih.gov/health/publications/so-stressed-out-fact-sheet#:~:text=What%20is%20stress%3F%20Stress%20is,repeatedly%20over%20a%20long%20time),
and recognizes that response as a multifaceted process (involving both
psychological perception *and* physiological changes). In summary, *the
official definition of stress in psychology is broader and more neutral
than the everyday notion*: it emphasizes **stress as a process**
(perceiving a challenge and responding to
it)[\[9\]](https://www.psychologytoday.com/us/basics/stress#:~:text=Reviewed%20by%20Psychology%20Today%20Staff),
whereas colloquially "stress" often just means the unpleasant feeling of
stress. Throughout this report, we use "stress" in the scientific sense
-- referring to the psychophysiological stress response -- while being
mindful that our ultimate goal is often to detect the negative,
excessive form of stress that people concern themselves with in daily
life.

## How is Stress Measured? From Cortisol to Conductance

To study stress objectively, researchers have established certain
**biological markers** of the stress response. Arguably the **"gold
standard" measure of stress is the hormone cortisol**, often called the
*stress hormone*. Cortisol is released by the adrenal glands as part of
the hypothalamic--pituitary--adrenal (HPA) axis activation under stress.
In laboratory settings, stress is frequently quantified via cortisol
levels in blood, saliva, or urine. For example, in the well-known Trier
Social Stress Test, a rise in salivary cortisol is taken as an indicator
that the subject experienced significant stress. Cortisol has a clear
link to stress in the body -- indeed, one can define the **magnitude of
a stress response by the amount of stress-induced cortisol**
present[\[11\]](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2020.00039/full#:~:text=stress,aware%20of%20their%20stress%20levels).
However, relying on cortisol as a measure comes with practical
drawbacks. **Cortisol levels change slowly** relative to many stressors:
there is typically a lag of \~20--30 minutes from the onset of a
stressful event to the peak in cortisol
secretion[\[12\]](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2020.00039/full#:~:text=It%20is%20generally%20accepted%20that,1992%3B%20Gunnar%20and%20Quevedo%2C%202007).
This means cortisol is not well-suited for real-time or high-resolution
monitoring of stress. Moreover, collecting cortisol usually requires
invasive or intrusive procedures (drawing blood, or repeatedly
collecting saliva samples) which, as our colleague jokingly noted, would
be *"terrible -- practically draining people's blood -- in a psych
study"*. It's simply not feasible to frequently invasively sample
hormones to track a person's stress over time.

Given these issues, researchers often use **alternative physiological
signals as proxies for stress that are more convenient to measure
continuously**. One of the most common is the **Galvanic Skin Response
(GSR)**, also known as skin conductance or **Electrodermal Activity
(EDA)**. GSR is a property of the skin that changes with sweat gland
activity and is controlled by the sympathetic nervous system (the
"fight-or-flight" branch). Unlike cortisol, changes in GSR occur *within
seconds* of stress onset, providing a near-instantaneous readout of
sympathetic
activation[\[12\]](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2020.00039/full#:~:text=It%20is%20generally%20accepted%20that,1992%3B%20Gunnar%20and%20Quevedo%2C%202007).
Furthermore, measuring GSR is non-invasive -- typically done by
attaching simple electrodes to the surface of the skin (often the
fingers or palm). Thus, **GSR offers much better time resolution and
practicality** for stress monitoring than hormonal measures. In fact,
GSR has become a de facto standard in psychophysiology studies of stress
and emotion: it is widely used as an **objective index of arousal** in
lie detector tests, therapy research, user experience studies, etc.
While it is not a direct hormone measurement, GSR correlates with
stress-related sympathetic arousal and can serve as a *surrogate
measure* of stress level. The trade-off, as we will discuss, is that GSR
(and similar measures like heart rate) captures the **"immediate" stress
response** governed by neural signals, whereas cortisol captures the
**longer-term hormonal stress response** -- both are facets of stress,
but GSR responds faster and with less specificity to the nature of the
stressor.

# Galvanic Skin Response (GSR) and Stress

## Origin of the GSR Signal

What exactly is **Galvanic Skin Response** measuring, and why does it
reflect stress? Physiologically, the GSR signal originates from the
activity of the **eccrine sweat glands in the skin**, which are
controlled by the sympathetic nervous system. When we experience stress
or strong emotions, the sympathetic nerves fire and cause the sweat
glands (especially on the palms, fingers, and soles) to increase
secretion. Even if only minuscule amounts of sweat are released (not
necessarily visible perspiration), this added moisture on the skin
**lowers the electrical resistance of the skin**. In other words, **it
increases skin conductance**. GSR sensors typically apply a tiny
constant voltage across two points on the skin and measure how
conductance changes over time. During a stress response, as sweat gland
activity goes up, conductance can spike by a noticeable
amount[\[13\]](https://en.wikipedia.org/wiki/Electrodermal_activity#:~:text=The%20traditional%20theory%20of%20EDA,of%20the%20skin%20potential%20is)[\[14\]](https://www.sciencedirect.com/topics/medicine-and-dentistry/electrodermal-activity#:~:text=Topics%20www,sympathetic%20nerve%20on%20sweat%20glands).
In this way, **EDA is essentially a direct readout of sympathetic
nervous system activation**: as one textbook puts it, *"Electrodermal
activity...reflects the activity of the sympathetic nerve on sweat
glands."*[\[14\]](https://www.sciencedirect.com/topics/medicine-and-dentistry/electrodermal-activity#:~:text=Topics%20www,sympathetic%20nerve%20on%20sweat%20glands)
It is a unique psychophysiological measure in that it has **no
significant parasympathetic (calming) input** -- it's purely a
sympathetic arousal
indicator[\[13\]](https://en.wikipedia.org/wiki/Electrodermal_activity#:~:text=The%20traditional%20theory%20of%20EDA,of%20the%20skin%20potential%20is).
The **traditional theory of GSR** dates back over a century and holds
true: *sweating (and hence skin conductance) varies with emotional state
and arousal
level*[\[13\]](https://en.wikipedia.org/wiki/Electrodermal_activity#:~:text=The%20traditional%20theory%20of%20EDA,of%20the%20skin%20potential%20is).
For example, a sudden fright or mental stressor causes an almost
immediate surge in skin conductance due to a burst of sympathetic
activity triggering sweat release. (Interestingly, research has found a
few edge cases -- e.g. people with no sweat glands still show some skin
potential changes -- suggesting there are additional ionic mechanisms at
play[\[15\]](https://en.wikipedia.org/wiki/Electrodermal_activity#:~:text=a%20measure%20of%20emotional%20and,A%20good%20way%20to).
But sweat gland activity remains the primary driver of the GSR signal in
normal cases.)

To measure GSR in practice, one usually places two electrodes on a
person\'s skin (commonly on two fingers of one hand). A small constant
current is passed, and the device (often a dedicated amplifier or a
wearable unit) records the dynamic changes in conductance. Modern
wearable GSR sensors make this quite convenient. For instance, the
**Shimmer3 GSR+** is a compact wireless device designed for research: it
attaches to the fingers with electrodes and samples the skin conductance
at up to 128 Hz, streaming the data via
Bluetooth[\[16\]](https://www.mdpi.com/2076-3417/14/24/11997#:~:text=Measurements%20were%20performed%20using%20Shimmer,to%20assess%20the%20galvanic%20skin)[\[17\]](https://www.mdpi.com/2076-3417/14/24/11997#:~:text=Shimmer%20device%2C%20attached%20to%20the,time%20via%20Bluetooth%20to%20a).
Such devices provide pre-amplification and digitization of the GSR
signal on the unit, yielding high-quality data for analysis. *(For
completeness, note that GSR is also sometimes measured as skin
resistance or skin potential, but skin conductance is the most common
metric. "Electrodermal activity" is an umbrella term covering all
these.)*

## Properties of the GSR Signal

The GSR signal has distinct characteristics that differentiate it from
other physiological signals like heart rate or brain waves. **In terms
of amplitude**, skin conductance is typically measured in microsiemens
(µS, since it's a conductance). A calm baseline skin conductance level
might be on the order of 1--10 µS, and emotional stimuli elicit **phasic
conductance responses** that often range from about **0.1 up to 2 or
more µS** in
magnitude[\[18\]](https://www.researchgate.net/figure/Example-of-a-typical-SCR-Following-stimulus-onset-there-is-a-1-to-3-s-latency-before_fig1_232543769#:~:text=A%20typical%20SCR%20is%20shown,0%20%E2%90%AE%20S).
In highly aroused or sweaty individuals, peaks can be larger (several
µS), but for most people a significant skin conductance response (SCR)
might be, say, a 0.5 µS increase from baseline. The **time course** of
GSR changes is relatively slow. A typical SCR to a sudden stimulus has a
*latency of about 1--3 seconds* (after the stimulus onset, the
conductance begins rising) and reaches its **peak after about another
1--3
seconds**[\[18\]](https://www.researchgate.net/figure/Example-of-a-typical-SCR-Following-stimulus-onset-there-is-a-1-to-3-s-latency-before_fig1_232543769#:~:text=A%20typical%20SCR%20is%20shown,0%20%E2%90%AE%20S).
Thus, the rise time of an SCR is a few seconds, and then it recovers
back to baseline over a period of 5--20 seconds, depending on the person
and stimulus. This is much slower than, for example, changes in heart
rate or EEG signals, which occur on a sub-second scale. In fact,
researchers note that *"the SCR is a relatively slow-moving response"*
compared to other physiological
measures[\[18\]](https://www.researchgate.net/figure/Example-of-a-typical-SCR-Following-stimulus-onset-there-is-a-1-to-3-s-latency-before_fig1_232543769#:~:text=A%20typical%20SCR%20is%20shown,0%20%E2%90%AE%20S).
Because of this, **the meaningful frequency content of GSR signals lies
in the low-frequency range**. Most of the variance in an EDA signal is
below 1 Hz. Studies performing spectral analysis have found that **the
strongest power in the skin conductance signal occurs below \~0.5 Hz**
(often in the 0.1 to 0.2 Hz band for phasic
activity)[\[19\]](https://pubmed.ncbi.nlm.nih.gov/27059225/#:~:text=PubMed%20pubmed,the%20prescribed%20band%20for%20HRVLF).
Essentially, GSR is dominated by very slow oscillations and discrete
responses rather than high-frequency fluctuations.

Researchers often decompose the GSR signal into two components: a
**tonic level** (also called Skin Conductance Level, SCL) which is the
baseline conductance that drifts slowly, and **phasic responses** (Skin
Conductance Responses, SCRs) which are those short bursts or peaks tied
to specific events or stimuli. The tonic level can vary over minutes
(e.g. higher if someone is generally more aroused or sweating more due
to heat), whereas the phasic SCRs are time-locked to discrete moments of
arousal. This decomposition is useful because, for instance, one might
measure the *frequency of SCR peaks* as an indicator of how often the
person is being psychologically aroused (e.g. number of "stress
responses" per minute), or the *amplitude of a specific SCR* to a known
stimulus as a measure of reactivity.

In summary, **GSR signals are characterized by amplitudes on the order
of fractions of a microsiemens to a few µS**, **slow waveforms** with
peaks taking seconds, and main spectral energy in the very low frequency
range (tens of seconds per
cycle)[\[18\]](https://www.researchgate.net/figure/Example-of-a-typical-SCR-Following-stimulus-onset-there-is-a-1-to-3-s-latency-before_fig1_232543769#:~:text=A%20typical%20SCR%20is%20shown,0%20%E2%90%AE%20S)[\[19\]](https://pubmed.ncbi.nlm.nih.gov/27059225/#:~:text=PubMed%20pubmed,the%20prescribed%20band%20for%20HRVLF).
Because of these properties, GSR data is typically sampled at modest
rates (e.g. 10--100 Hz is plenty to capture it) and often analyzed with
smoothing or peak-detection algorithms rather than, say, fine Fourier
analysis. (It's worth noting that despite sampling up to 128 Hz or more
being possible, many studies down-sample EDA to around 10 Hz because
faster sampling yields little new information for such a slow
signal[\[20\]](https://www.utwente.nl/en/bmslab/infohub/shimmer3-gsr/#:~:text=1,Report%20the%20associated%20skin%20conductance).)

## Interpretation of GSR: What Does It Tell Us?

GSR is widely interpreted as a **measure of emotional and physiological
arousal**. When we see an increase in someone's skin conductance, we
infer that their sympathetic nervous system was activated -- which could
be due to stress, excitement, fear, startle, pain, or any state that
involves arousal. Indeed, *"skin conductance response (SCR) serves as a
dependable marker of sympathetic activation used to measure emotional
arousal."*[\[21\]](https://pubmed.ncbi.nlm.nih.gov/39488879/#:~:text=,used%20to%20measure%20emotional%20arousal)
It's important to emphasize that **GSR is *not* specific to any
particular emotion**. Rather, it indexes the intensity of the emotion
(or attention or effort) -- the **arousal dimension**, not the valence.
A joyous surprise and a terror fright can both produce a similar spike
in GSR. As one source succinctly states, *EDA shows the intensity of
arousal, but not the valence; thus, context is needed to interpret
it*[\[22\]](https://www.sciencedirect.com/topics/computer-science/skin-conductance#:~:text=Skin%20Conductance%20,important%20to%20couple%20SCR).
Because of this, GSR is often used in combination with other measures.
For example, a study might use facial expressions or self-report to
gauge whether an emotion is positive or negative, and use GSR to
quantify how strongly the person was feeling it.

Nonetheless, **GSR is very sensitive to a broad range of psychologically
significant events**. Novel or significant stimuli (a loud sound, an
emotionally charged image, the anticipation of an exam) will typically
elicit a conductance
response[\[23\]](https://www.researchgate.net/figure/Example-of-a-typical-SCR-Following-stimulus-onset-there-is-a-1-to-3-s-latency-before_fig1_232543769#:~:text=sufficient%20time%20for%20the%20response,are%20neurocircuits%20influencing%20the%20SCR).
GSR has been used to detect moments of surprise, fear conditioning
responses, sexual arousal, cognitive workload changes, and of course
stress from mental tasks. In biofeedback and psychophysiology, the
number of spontaneous GSR fluctuations in a period can even reflect
someone's general stress level or anxiety (more frequent SCRs at rest
often correlate with higher anxiety). Because *so many factors can
influence GSR*, one must be cautious -- for instance, an SCR could
indicate a startle at a noise unrelated to the experimental task, rather
than the task itself. But in controlled settings, GSR provides a robust
window into the **"emotional sweat" of the sympathetic system**, giving
researchers a quantitative handle on the otherwise hidden bodily changes
accompanying psychological processes.

As an example of interpretation: if during a public speaking task a
subject's GSR steadily climbs and shows frequent peaks, we interpret
that as **high sympathetic arousal consistent with stress** (assuming no
other factors like temperature change). On the other hand, if their GSR
stays low and flat, we infer low arousal -- perhaps the person is calm
or not emotionally engaged. Importantly, we wouldn't know *why* it's
high or low from GSR alone (they could be excited rather than fearful),
but within an experimental context we usually have an idea (public
speaking is intended to induce stress). Thus, **GSR is extremely useful
for *detecting the presence and magnitude of an emotional response***,
even though it doesn't tell us the qualitative nature of that emotion by
itself[\[22\]](https://www.sciencedirect.com/topics/computer-science/skin-conductance#:~:text=Skin%20Conductance%20,important%20to%20couple%20SCR).

## Limitations of GSR in Stress Measurement

Despite its usefulness, GSR has several **limitations and
considerations** to keep in mind. Firstly, as noted, **GSR is not
emotion-specific** -- it's an arousal meter, not a stress-or-joy meter.
This means that interpretation requires context and often other
measures. An increased skin conductance might indicate stress, or it
might indicate excitement; **the context and concurrent observations are
needed to
disambiguate**[\[24\]](https://noldus.com/blog/what-is-galvanic-skin-response#:~:text=While%20GSR%20is%20a%20powerful,analysis%20and%20heart%20rate%20monitoring).
When using GSR to assess "stress," researchers must design experiments
carefully (e.g. using tasks known to induce stress rather than positive
excitement) or combine GSR with subjective reports.

Secondly, **individual differences** can affect GSR readings. People
vary in their skin conductance baselines and responsiveness. Some
individuals (called "non-responders") naturally show almost no GSR
changes even when they report feeling stressed -- possibly due to less
sweat gland reactivity. Others have higher tonic levels or larger
responses. Thus, comparisons across individuals can be tricky; often
experiments look at changes from each person's baseline or use
within-subject designs.

Thirdly, **environmental and physiological factors can confound GSR**.
Room temperature and humidity, for example, influence skin moisture and
can drive slow shifts in conductance unrelated to psychological
state[\[25\]](https://noldus.com/blog/what-is-galvanic-skin-response#:~:text=methods%2C%20like%20facial%20expression%20analysis,and%20heart%20rate%20monitoring).
A hot room might raise baseline GSR due to thermoregulatory sweating.
The participant's hydration level or recent physical activity can also
alter skin conductance (if you just ran and are sweating, your GSR will
be high). Researchers must control or at least record such factors --
usually by keeping the room comfortable, asking participants to sit
still, etc. Motion artifacts are another consideration: if electrodes
slip or if the person moves their hand vigorously, the GSR signal can
spike erroneously. Good experimental protocols include ensuring
electrodes make stable contact and sometimes cleaning the skin to
maintain consistent contact.

Another limitation is that **GSR, being a slow signal, has limited time
precision**. If stressors occur in rapid succession, the individual SCR
responses can overlap. The latency (1--3 s) means GSR can't distinguish
events that happen within a second of each other. Researchers allow
buffer time between stimuli for GSR to rise and fall.

Finally, unlike some signals that can be localized (e.g. one can measure
brain activity from different regions), **GSR is usually a global or
generalized measure**. It doesn't tell you *where* on the body the
arousal is manifesting (since it's typically measured at one hand).
However, research has shown that measuring at different sites (palms vs
feet, left vs right hand) can sometimes yield slightly different
sensitivities, and using multiple GSR channels could add information --
but this is not common practice.

In summary, **the key limitations of GSR are its non-specificity and
susceptibility to external influences**. It *"effectively measures the
intensity of emotional arousal but not the type of emotion itself"*, as
one review put
it[\[26\]](https://www.ignitec.com/insights/what-galvanic-skin-response-technology-tells-us-about-emotional-arousal/#:~:text=arousal%20www,excitement%20vs).
Additionally, factors like **environment, movement, and individual
physiology can affect readings**, so those must be accounted for to
avoid misinterpreting the
data[\[24\]](https://noldus.com/blog/what-is-galvanic-skin-response#:~:text=While%20GSR%20is%20a%20powerful,analysis%20and%20heart%20rate%20monitoring).
Despite these caveats, GSR remains a valuable tool, especially when used
as part of a multi-modal assessment of stress (for example, alongside
heart rate, facial expression, or self-report, to build a complete
picture).

# Thermal Imaging for Stress Detection

## From Skin Physiology to Thermal Signals

We've seen that stress triggers physiological responses like sweating
and changes in blood flow. Many of these responses have a **thermal
signature** -- that is, they affect the temperature distribution of the
body. **Thermal imaging (infrared imaging)** detects the natural
infrared radiation emitted by the skin to measure surface temperature
without contact. The idea of using thermal cameras for stress or emotion
detection is that some of the same sympathetic activations that GSR
picks up (sweat, blood vessel changes) should also manifest as
temperature changes on the skin's surface.

One well-documented thermal indicator of stress is the change in facial
blood flow. When the sympathetic "fight-or-flight" response kicks in,
one effect can be **peripheral vasoconstriction** -- blood is redirected
from the skin to the core organs. In the face, for instance, researchers
have observed that during acute stress or startle, the **temperature of
the nose tip and surrounding areas tends to drop** markedly, due to
reduced blood perfusion in the skin
there[\[27\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=of%20providing%20the%20measures%20of,the%20tip%20of%20the%20nose).
This is essentially the thermal correlate of stress: cooler nose/face
because the blood vessels constrict (the opposite of blushing, which is
vasodilation). A high-resolution thermal camera can capture this change.
In fact, a study by Pavlidis et al. famously demonstrated a "thermal
imaging lie detector" that tracked periorbital (around the eyes)
temperature changes associated with the stress of lying. Similarly,
**nasal skin temperature has been used as an index of stress**, with
findings that it decreases under mental workload or
anxiety[\[27\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=of%20providing%20the%20measures%20of,the%20tip%20of%20the%20nose).

Sweat itself can have a thermal effect too. When sweat evaporates from
the skin, it cools the skin (evaporative cooling). So, if a person
starts sweating in, say, the forehead or palms due to stress, a thermal
camera might detect a slight drop in skin temperature in those regions.
Some researchers have looked at **perinasal perspiration**: under
stress, humans often sweat on the nose area and upper lip, which in
thermal images shows up as a cooling (because evaporation consumes
heat).

Beyond localized effects, **breathing pattern changes** with stress can
also be detected thermally -- e.g. people under stress might breathe
faster or irregularly, and a thermal camera can monitor breathing by the
cyclic temperature changes at the nostrils. Thermal imaging has even
been used to derive heart rate, by tracking subtle pulsatile warming of
the skin due to blood flow.

In summary, **stress-induced sympathetic activation leads to measurable
thermal changes: cooler skin in some areas (due to vasoconstriction and
sweat evaporation) and possibly warming in core areas (if blood is
shunted)**. These changes are often most evident in the face (which is
convenient, since a camera can easily view a person's face). Thus, it
stands to reason -- as our colleague suggested -- that if GSR is sensing
a "capillary dilation or constriction" process, a **thermal camera
should be able to detect that process in the form of temperature
changes**. Indeed, modern research supports this: *"Stressful conditions
were found to trigger a sympathetically driven vasoconstriction of the
blood vessels in the skin, which is reflected by a drop in the
temperature of the tip of the
nose."*[\[27\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=of%20providing%20the%20measures%20of,the%20tip%20of%20the%20nose)
Thermal imaging is, in effect, another window into the autonomic state
of a person, just via heat instead of electrical conductance.

## Thermal Imaging Technology and Its Characteristics

**Thermal cameras** used in human research operate in the long-wave
infrared range (typically 8--14 µm wavelength) and produce a
temperature-map (thermogram) of the scene. When applying them to
physiology, there are some important specifications: **spatial
resolution**, **thermal sensitivity**, and **temporal resolution**
(frame rate). Compared to regular RGB cameras, thermal cameras generally
have lower resolution and frame rates, due to the physics and cost of
infrared sensors. However, many are sufficient for capturing the
relatively slow thermal changes of interest.

For instance, a research-grade thermal camera like the FLIR T640 offers
a resolution of 640×480 pixels and a thermal sensitivity (Noise
Equivalent Temperature Difference, NETD) better than **0.04 °C** (i.e.
it can discern temperature differences as small as 0.04
°C)[\[28\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=distribution%20was%20unobtrusively%20acquired%20through,wave%20infrared%E2%80%94LWIR%29.%20Additionally%2C%20standard%20RGB).
In one stress study, this camera was used at **5 Hz frame rate** to
monitor facial temperature, which is adequate since thermal changes in
stress occur over
seconds[\[28\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=distribution%20was%20unobtrusively%20acquired%20through,wave%20infrared%E2%80%94LWIR%29.%20Additionally%2C%20standard%20RGB).
On the other hand, more portable and affordable thermal sensors have
lower resolution but can have higher frame rates. A good example is the
**Topdon TC001**, a smartphone-based thermal camera (shown below) which
has a 256×192 IR resolution and runs up to **25 Hz** frame
rate[\[29\]](https://mechanicsuperstore.com/products/topdon-usa-tc001-android-devices-portable-thermal-imaging-camera#:~:text=Spectral%20Range%208,4~302%C2%B0F%29%2C%20150%C2%B0C~550%C2%B0C%20%28302~1022%C2%B0F).
Despite its lower pixel count, it still achieves about **0.04 °C thermal
sensitivity** and can detect subtle temperature variations on human
skin[\[29\]](https://mechanicsuperstore.com/products/topdon-usa-tc001-android-devices-portable-thermal-imaging-camera#:~:text=Spectral%20Range%208,4~302%C2%B0F%29%2C%20150%C2%B0C~550%C2%B0C%20%28302~1022%C2%B0F).
The **temperature range** of interest for human use is roughly 20--40 °C
(room to body temperature), well within these devices' measurement span.
High-end cameras may span a wider range (e.g. --20 to 150 °C) but for
stress we only care about skin temps.

*Example of a portable thermal imaging device (Topdon TC001) that can
attach to a smartphone. Such cameras capture infrared images of the
skin, revealing temperature patterns. Researchers use them to detect
stress-induced temperature changes (like cooler areas from
vasoconstriction). The TC001 shown has a 256×192 IR sensor and operates
at
25 Hz[\[29\]](https://mechanicsuperstore.com/products/topdon-usa-tc001-android-devices-portable-thermal-imaging-camera#:~:text=Spectral%20Range%208,4~302%C2%B0F%29%2C%20150%C2%B0C~550%C2%B0C%20%28302~1022%C2%B0F).*

**Temporal resolution (frame rate)** matters if one wants to capture
things like heart or breathing rate from thermal. Many thermal cameras,
due to export restrictions, are capped at 9 Hz or 30 Hz. A 9 Hz camera
can still capture slow stress-related shifts (nose cooling over 10
seconds, etc.), but might miss rapid changes. The Topdon device at 25 Hz
or others at 30 Hz are sufficient to even measure pulse or respiration
oscillations (which are on the order of 1--2 Hz at most). In general,
stress thermal signatures are slow (a nose might steadily drop 1--2 °C
over a minute of stress). So even low frame rates can detect the overall
trend, though higher frame rates enable applying signal processing (e.g.
filtering out noise, capturing faster physiological rhythms if needed).

**Noise** in thermal imaging comes from both the sensor and the
environment. The NETD of \~0.04 °C mentioned means the camera can, under
good conditions, distinguish very small temperature differences. This is
important because the thermal effects of stress might be on the order of
a few tenths of a degree change. For example, a nose tip might drop by
0.5 °C when a person becomes anxious. A camera with 0.05 °C sensitivity
can catch that. Environmental factors (airflow, ambient temperature
shifts) can introduce noise too -- e.g. a breeze on the face could cool
it independent of stress. Thus, similar to GSR, experimental control is
needed: one would ideally do thermal measurements in a stable indoor
climate. Thermal image data also often requires calibration or at least
consistent distance/emissivity settings to get accurate readings of skin
temperature.

In terms of **methodology**, using thermal imaging for stress is
completely contactless and can be done unobtrusively (a camera at some
distance). It provides a rich 2D map of temperatures. Researchers
typically focus analysis on specific regions known to change (face
regions: nose, forehead, periorbital; or sometimes hands). There are
algorithms to track the face and compute the average temperature of the
nose tip, etc., over time and then correlate those with stress events or
levels.

**Advantages:** Thermal imaging of stress is promising because it
directly measures a *biophysical consequence* of stress (heat changes)
in a way that is easy for humans to interpret as well -- e.g. you can
literally *see* someone's nose get colder on the thermal video when
they're stressed. It has been noted that a purely thermal-based stress
monitor could be very comfortable and unobtrusive compared to wearing
multiple
sensors[\[30\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=match%20at%20L1012%20contactless%20thermal,based%20systems).
Indeed, one study emphasized that a *"contactless thermal imaging system
for stress recognition would have the advantages of being more
comfortable with respect to intrusive contact-based
systems."*[\[31\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=contactless%20thermal%20imaging%20can%20still,based%20systems)
This is a key reason thermal methods have gained traction: they offer a
way to monitor physiological stress responses without wires or
discomfort.

**Limitations:** On the flip side, thermal imaging can be sensitive to
ambient conditions (as mentioned) and typically requires line-of-sight
to the subject's skin. If the person covers their face or the
lighting/reflectivity conditions are poor (thermal cameras need a clear
view and are not affected by lighting but can be affected by reflective
surfaces or glasses, etc.), data quality suffers. Also, thermal cameras
used to be quite expensive, though prices are coming down with devices
like the Topdon (hundreds of dollars rather than tens of thousands). The
**spatial resolution** is lower than visible cameras, so pinpointing
small regions (like a very small facial feature) might be limited by
pixel size at a distance.

In practice, current research has shown that **thermal imaging can
detect stress with reasonable accuracy**. For example, one study
achieved good stress classification by using just facial thermal
features (like the nose temp drop and forehead temp changes) and feeding
those into a machine learning
model[\[32\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=Moreover%2C%20we%20investigated%20the%20potential,nasal)[\[33\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=of%20providing%20the%20measures%20of,the%20tip%20of%20the%20nose).
This underscores that the physiological signal is indeed present in the
thermal domain. Thermal is a contactless technique, so it aligns with
the earlier discussion of being non-intrusive and even allows
**monitoring multiple people's stress simultaneously** (imagine an IR
camera scanning a whole group for stress cues, which has applications in
security or classroom settings).

# Machine Learning and the Potential of RGB Video for Stress Detection

Thermal imaging has shown clear advantages for observing stress-related
changes (humans can visually see heat patterns corresponding to stress).
However, an intriguing question arises: **Do we truly need a thermal
camera, or could a normal RGB camera (visible light) also pick up stress
indicators with the help of machine learning?** This question is
motivated by the fact that **machines can often detect patterns that are
invisible to the naked human eye**. Over the years, advances in computer
vision and machine learning have revealed that algorithms can amplify
and extract subtle physiological signals from regular video.

One striking example is the detection of heartbeat and breathing using a
standard camera. It turns out that each heartbeat causes tiny changes in
skin color (due to blood flow) and minute motions in the body. These
changes are far too subtle for a person to see -- a face won't visibly
flush with each pulse under normal conditions. But algorithms like
*Eulerian Video Magnification* can amplify those tiny color fluctuations
to make the pulse
visible[\[34\]](https://medium.com/augmented-startups/heart-rate-detection-using-eulerian-video-magnification-yolor-49818dd1b2f5#:~:text=Hao,tiniest%20motions%20and%20color%20changes)[\[35\]](https://medium.com/augmented-startups/heart-rate-detection-using-eulerian-video-magnification-yolor-49818dd1b2f5#:~:text=them%20more%20obvious).
Essentially, *"there is a world of motion (and color change) too subtle
for the human eye, that can be seen by a regular camera"* when processed
appropriately[\[36\]](https://medium.com/augmented-startups/heart-rate-detection-using-eulerian-video-magnification-yolor-49818dd1b2f5#:~:text=that%20there%20is%20a%20world,the%20help%20of%20some%20examples).
Researchers Wu et al. demonstrated that by focusing on the frequency
band of human heart rate in a video, one can reveal the heartbeat as a
rhythmic color change on the
face[\[37\]](https://medium.com/augmented-startups/heart-rate-detection-using-eulerian-video-magnification-yolor-49818dd1b2f5#:~:text=For%20example%2C%20there%20is%20a,heart%20rate%20of%20an%20individual).
Similarly, the slight rise and fall of a sleeping baby's chest, or the
pulse in someone's wrist, can be algorithmically extracted from standard
videos[\[38\]](https://medium.com/augmented-startups/heart-rate-detection-using-eulerian-video-magnification-yolor-49818dd1b2f5#:~:text=In%20the%20GIF%20above%2C%20there,to%20be%20almost%20completely%20still)[\[39\]](https://medium.com/augmented-startups/heart-rate-detection-using-eulerian-video-magnification-yolor-49818dd1b2f5#:~:text=to%20reveal%20the%20tiniest%20motions,and%20color%20changes).
These findings underscore that **RGB cameras *do* capture rich
physiological information (blood flow, respiration, etc.), but it's
hidden in plain sight -- requiring computational methods to uncover**.

Applying this idea to stress: If stress causes changes like altered
blood flow or subtle facial cues (e.g. maybe a slight blanching of the
skin from vasoconstriction, or micro-expressions of discomfort), an AI
might detect patterns across the RGB frames that correlate with stress,
even if those patterns are not obvious to a human viewer. For instance,
a machine learning model might pick up on a combination of slight pallor
in the nose area, increased sheen on the skin (from perspiration), and
faster head movements (from anxiety), which together signal stress. None
of these might be decisively noticeable to a person watching the video,
but statistically, the model can separate stressful versus non-stressful
instances. In fact, initial studies have started exploring **fusion of
RGB and thermal data for stress detection**, and some results indicate
that RGB video alone, when processed with advanced algorithms, can
approach the accuracy of
thermal[\[40\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC6477570/#:~:text=Instant%20Stress%3A%20Detection%20of%20Perceived,physiological%20measurements%20for%20stress).
For example, remote photoplethysmography (rPPG) from an RGB camera can
yield heart rate and heart rate variability, which are known stress
indicators (heart rate variability tends to decrease under stress).
Additionally, **facial expression analysis** from RGB video can detect
brow furrows, lip presses, or other micro-expressions tied to stress.

One reason thermal imaging has been popular in research is because *the
stress effects are human-visible in that modality* -- a researcher can
literally see the temperature change in thermal, which is compelling.
With RGB, the changes are not as directly visible, which historically
made it seem less viable for this purpose. But the **lesson from modern
AI is that lack of human-visibility does not equal lack of signal**.
Machines can exploit subtle cues beyond our
perception[\[36\]](https://medium.com/augmented-startups/heart-rate-detection-using-eulerian-video-magnification-yolor-49818dd1b2f5#:~:text=that%20there%20is%20a%20world,the%20help%20of%20some%20examples).
As a parallel, consider that AI models have learned to diagnose medical
conditions from normal photographs or scans where doctors see nothing
obvious -- because the AI finds minute patterns. In the context of
stress, an algorithm might learn the **complex pattern of color shifts**
in the face that correspond to vasoconstriction. It might also use the
fact that under stress people's **breathing changes** (which can be
detected by tiny movements of the chest or shoulders in the RGB video).
There is ongoing research into using **standard cameras for contactless
vitals measurement and stress
inference**[\[41\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC10721846/#:~:text=,BVP%29%20signal%2C%20heart)[\[42\]](https://www.researchgate.net/publication/357132971_Detecting_Human_Emotions_Through_Physiological_Signals_Using_Machine_Learning#:~:text=Detecting%20Human%20Emotions%20Through%20Physiological,the%20frame%20of%20the),
and results are promising.

Therefore, the research question posed is: *Does an ordinary RGB camera
contain sufficient information to measure stress, such that a thermal
camera may not be strictly necessary?* The hypothesis is that **with
appropriate machine learning algorithms, we might extract stress
signatures from RGB video alone** -- for example, by combining signals
like remote pulse (from face color changes), remote breathing rate (from
motion), and perhaps facial expression or perspiration cues. If
successful, this would mean one could achieve contactless stress
monitoring with just a webcam, which is even more accessible than
thermal. Indeed, one recent study combined visible and thermal imagery
and found that machine learning on the visible spectrum added value,
suggesting that the visible camera was contributing useful info beyond
what the thermal
provided[\[43\]](https://www.mdpi.com/2072-4292/13/9/1785#:~:text=Integration%20of%20Visible%20and%20Thermal,the%20individual%20visible%20or).

It's worth noting that **thermal cameras remain advantageous in
low-light or no-light conditions** (they don't require illumination) and
for certain direct measurements of skin temperature. But RGB cameras are
ubiquitous (every laptop and phone has one) and capture higher
resolution images. The trade-off is that the signal is more implicit.

In conclusion, machine learning opens the door to leveraging **RGB video
as a contactless sensor for stress**, potentially reducing the need for
specialized thermal equipment. As our colleague speculated, *thermal
imaging might be more widely researched simply because the effects are
easier for humans to see, but an AI might not need the data to be
human-obvious* to make use of it. We already have proof-of-concept in
related domains that **AI can detect "invisible" physiological
patterns** -- for instance, an algorithm can reveal a person's heart
rate by amplifying tiny color fluctuations on their
face[\[35\]](https://medium.com/augmented-startups/heart-rate-detection-using-eulerian-video-magnification-yolor-49818dd1b2f5#:~:text=them%20more%20obvious),
akin to an imperceptible blush with each heartbeat. By the same token,
an algorithm might detect an *"invisible stress blush"* or other
composite pattern from an RGB feed. Going forward, this line of research
could yield **RGB-based stress monitoring systems** that work with just
a standard camera and smart algorithms, making stress detection
technology far more accessible.

------------------------------------------------------------------------

**References:** (Included as inline citations in the text
above)[\[1\]](https://www.mdpi.com/1424-8220/24/11/3484#:~:text=Emotion%20detection%20is%20a%20research,to%20transform%20various%20industries%20and)[\[6\]](https://colab.ws/articles/10.1049%2Fhtl.2014.0077#:~:text=Current%20technologies%20to%20allow%20continuous,The)[\[5\]](https://www.frontiersin.org/journals/communications-and-networks/articles/10.3389/frcmn.2021.636293/full#:~:text=RPM%20sensors%20can%20be%20broadly,video%2C%20sound%2C%20radar%2C%20and%20other)[\[8\]](https://www.nimh.nih.gov/health/publications/so-stressed-out-fact-sheet#:~:text=What%20is%20stress%3F%20Stress%20is,repeatedly%20over%20a%20long%20time)[\[10\]](https://www.nimh.nih.gov/health/publications/so-stressed-out-fact-sheet#:~:text=,cause%20you%20to%20lose%20sleep)[\[9\]](https://www.psychologytoday.com/us/basics/stress#:~:text=Reviewed%20by%20Psychology%20Today%20Staff)[\[11\]](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2020.00039/full#:~:text=stress,aware%20of%20their%20stress%20levels)[\[12\]](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2020.00039/full#:~:text=It%20is%20generally%20accepted%20that,1992%3B%20Gunnar%20and%20Quevedo%2C%202007)[\[13\]](https://en.wikipedia.org/wiki/Electrodermal_activity#:~:text=The%20traditional%20theory%20of%20EDA,of%20the%20skin%20potential%20is)[\[14\]](https://www.sciencedirect.com/topics/medicine-and-dentistry/electrodermal-activity#:~:text=Topics%20www,sympathetic%20nerve%20on%20sweat%20glands)[\[18\]](https://www.researchgate.net/figure/Example-of-a-typical-SCR-Following-stimulus-onset-there-is-a-1-to-3-s-latency-before_fig1_232543769#:~:text=A%20typical%20SCR%20is%20shown,0%20%E2%90%AE%20S)[\[19\]](https://pubmed.ncbi.nlm.nih.gov/27059225/#:~:text=PubMed%20pubmed,the%20prescribed%20band%20for%20HRVLF)[\[22\]](https://www.sciencedirect.com/topics/computer-science/skin-conductance#:~:text=Skin%20Conductance%20,important%20to%20couple%20SCR)[\[24\]](https://noldus.com/blog/what-is-galvanic-skin-response#:~:text=While%20GSR%20is%20a%20powerful,analysis%20and%20heart%20rate%20monitoring)[\[27\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=of%20providing%20the%20measures%20of,the%20tip%20of%20the%20nose)[\[28\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=distribution%20was%20unobtrusively%20acquired%20through,wave%20infrared%E2%80%94LWIR%29.%20Additionally%2C%20standard%20RGB)[\[29\]](https://mechanicsuperstore.com/products/topdon-usa-tc001-android-devices-portable-thermal-imaging-camera#:~:text=Spectral%20Range%208,4~302%C2%B0F%29%2C%20150%C2%B0C~550%C2%B0C%20%28302~1022%C2%B0F)[\[31\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=contactless%20thermal%20imaging%20can%20still,based%20systems)[\[36\]](https://medium.com/augmented-startups/heart-rate-detection-using-eulerian-video-magnification-yolor-49818dd1b2f5#:~:text=that%20there%20is%20a%20world,the%20help%20of%20some%20examples)[\[35\]](https://medium.com/augmented-startups/heart-rate-detection-using-eulerian-video-magnification-yolor-49818dd1b2f5#:~:text=them%20more%20obvious),
etc.

------------------------------------------------------------------------

[\[1\]](https://www.mdpi.com/1424-8220/24/11/3484#:~:text=Emotion%20detection%20is%20a%20research,to%20transform%20various%20industries%20and)
[\[2\]](https://www.mdpi.com/1424-8220/24/11/3484#:~:text=Accurate%20detection%20of%20emotions%20can,Thus%2C%20the%20significance%20of)
[\[3\]](https://www.mdpi.com/1424-8220/24/11/3484#:~:text=disorders%2C%20facilitate%20personalized%20learning%2C%20and,Thus%2C%20the%20significance%20of)
[\[4\]](https://www.mdpi.com/1424-8220/24/11/3484#:~:text=gaming%20and%20virtual%20reality,to%20transform%20various%20industries%20and)
Systematic Review of Emotion Detection with Computer Vision and Deep
Learning

<https://www.mdpi.com/1424-8220/24/11/3484>

[\[5\]](https://www.frontiersin.org/journals/communications-and-networks/articles/10.3389/frcmn.2021.636293/full#:~:text=RPM%20sensors%20can%20be%20broadly,video%2C%20sound%2C%20radar%2C%20and%20other)
[\[7\]](https://www.frontiersin.org/journals/communications-and-networks/articles/10.3389/frcmn.2021.636293/full#:~:text=certain%20advantages%20over%20them,video%2C%20sound%2C%20radar%2C%20and%20other)
Frontiers \| A Review on Wearable and Contactless Sensing for COVID-19
With Policy Challenges

<https://www.frontiersin.org/journals/communications-and-networks/articles/10.3389/frcmn.2021.636293/full>

[\[6\]](https://colab.ws/articles/10.1049%2Fhtl.2014.0077#:~:text=Current%20technologies%20to%20allow%20continuous,The)
Continuous non-contact vital sign monitoring in neonatal intensive care
unit \| CoLab

<https://colab.ws/articles/10.1049%2Fhtl.2014.0077>

[\[8\]](https://www.nimh.nih.gov/health/publications/so-stressed-out-fact-sheet#:~:text=What%20is%20stress%3F%20Stress%20is,repeatedly%20over%20a%20long%20time)
[\[10\]](https://www.nimh.nih.gov/health/publications/so-stressed-out-fact-sheet#:~:text=,cause%20you%20to%20lose%20sleep)
I'm So Stressed Out! Fact Sheet - National Institute of Mental Health
(NIMH)

<https://www.nimh.nih.gov/health/publications/so-stressed-out-fact-sheet>

[\[9\]](https://www.psychologytoday.com/us/basics/stress#:~:text=Reviewed%20by%20Psychology%20Today%20Staff)
Stress \| Psychology Today

<https://www.psychologytoday.com/us/basics/stress>

[\[11\]](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2020.00039/full#:~:text=stress,aware%20of%20their%20stress%20levels)
[\[12\]](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2020.00039/full#:~:text=It%20is%20generally%20accepted%20that,1992%3B%20Gunnar%20and%20Quevedo%2C%202007)
Frontiers \| Deriving a Cortisol-Related Stress Indicator From Wearable
Skin Conductance Measurements: Quantitative Model & Experimental
Validation

<https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2020.00039/full>

[\[13\]](https://en.wikipedia.org/wiki/Electrodermal_activity#:~:text=The%20traditional%20theory%20of%20EDA,of%20the%20skin%20potential%20is)
[\[15\]](https://en.wikipedia.org/wiki/Electrodermal_activity#:~:text=a%20measure%20of%20emotional%20and,A%20good%20way%20to)
Electrodermal activity - Wikipedia

<https://en.wikipedia.org/wiki/Electrodermal_activity>

[\[14\]](https://www.sciencedirect.com/topics/medicine-and-dentistry/electrodermal-activity#:~:text=Topics%20www,sympathetic%20nerve%20on%20sweat%20glands)
Electrodermal Activity - an overview \| ScienceDirect Topics

<https://www.sciencedirect.com/topics/medicine-and-dentistry/electrodermal-activity>

[\[16\]](https://www.mdpi.com/2076-3417/14/24/11997#:~:text=Measurements%20were%20performed%20using%20Shimmer,to%20assess%20the%20galvanic%20skin)
[\[17\]](https://www.mdpi.com/2076-3417/14/24/11997#:~:text=Shimmer%20device%2C%20attached%20to%20the,time%20via%20Bluetooth%20to%20a)
Galvanic Skin Response and Photoplethysmography for Stress Recognition
Using Machine Learning and Wearable Sensors

<https://www.mdpi.com/2076-3417/14/24/11997>

[\[18\]](https://www.researchgate.net/figure/Example-of-a-typical-SCR-Following-stimulus-onset-there-is-a-1-to-3-s-latency-before_fig1_232543769#:~:text=A%20typical%20SCR%20is%20shown,0%20%E2%90%AE%20S)
[\[23\]](https://www.researchgate.net/figure/Example-of-a-typical-SCR-Following-stimulus-onset-there-is-a-1-to-3-s-latency-before_fig1_232543769#:~:text=sufficient%20time%20for%20the%20response,are%20neurocircuits%20influencing%20the%20SCR)
Example of a typical SCR. Following stimulus onset, there is a 1 to 3
s\... \| Download Scientific Diagram

<https://www.researchgate.net/figure/Example-of-a-typical-SCR-Following-stimulus-onset-there-is-a-1-to-3-s-latency-before_fig1_232543769>

[\[19\]](https://pubmed.ncbi.nlm.nih.gov/27059225/#:~:text=PubMed%20pubmed,the%20prescribed%20band%20for%20HRVLF)
Power Spectral Density Analysis of Electrodermal Activity \... - PubMed

<https://pubmed.ncbi.nlm.nih.gov/27059225/>

[\[20\]](https://www.utwente.nl/en/bmslab/infohub/shimmer3-gsr/#:~:text=1,Report%20the%20associated%20skin%20conductance)
Shimmer3 GSR+ \| Infohub \| BMS Lab

<https://www.utwente.nl/en/bmslab/infohub/shimmer3-gsr/>

[\[21\]](https://pubmed.ncbi.nlm.nih.gov/39488879/#:~:text=,used%20to%20measure%20emotional%20arousal)
Skin conductance response and habituation to emotional facial \...

<https://pubmed.ncbi.nlm.nih.gov/39488879/>

[\[22\]](https://www.sciencedirect.com/topics/computer-science/skin-conductance#:~:text=Skin%20Conductance%20,important%20to%20couple%20SCR)
Skin Conductance - an overview \| ScienceDirect Topics

<https://www.sciencedirect.com/topics/computer-science/skin-conductance>

[\[24\]](https://noldus.com/blog/what-is-galvanic-skin-response#:~:text=While%20GSR%20is%20a%20powerful,analysis%20and%20heart%20rate%20monitoring)
[\[25\]](https://noldus.com/blog/what-is-galvanic-skin-response#:~:text=methods%2C%20like%20facial%20expression%20analysis,and%20heart%20rate%20monitoring)
What is Galvanic Skin Response? \| Noldus

<https://noldus.com/blog/what-is-galvanic-skin-response>

[\[26\]](https://www.ignitec.com/insights/what-galvanic-skin-response-technology-tells-us-about-emotional-arousal/#:~:text=arousal%20www,excitement%20vs)
What galvanic skin response tech tells us about emotional arousal

<https://www.ignitec.com/insights/what-galvanic-skin-response-technology-tells-us-about-emotional-arousal/>

[\[27\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=of%20providing%20the%20measures%20of,the%20tip%20of%20the%20nose)
[\[28\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=distribution%20was%20unobtrusively%20acquired%20through,wave%20infrared%E2%80%94LWIR%29.%20Additionally%2C%20standard%20RGB)
[\[30\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=match%20at%20L1012%20contactless%20thermal,based%20systems)
[\[31\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=contactless%20thermal%20imaging%20can%20still,based%20systems)
[\[32\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=Moreover%2C%20we%20investigated%20the%20potential,nasal)
[\[33\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=of%20providing%20the%20measures%20of,the%20tip%20of%20the%20nose)
Towards a Contactless Stress Classification Using Thermal Imaging

<https://www.mdpi.com/1424-8220/22/3/976>

[\[29\]](https://mechanicsuperstore.com/products/topdon-usa-tc001-android-devices-portable-thermal-imaging-camera#:~:text=Spectral%20Range%208,4~302%C2%B0F%29%2C%20150%C2%B0C~550%C2%B0C%20%28302~1022%C2%B0F)
Topdon USA TC001 (Android Devices) Portable Thermal Imaging Camera --
Mechanic Super Store

<https://mechanicsuperstore.com/products/topdon-usa-tc001-android-devices-portable-thermal-imaging-camera>

[\[34\]](https://medium.com/augmented-startups/heart-rate-detection-using-eulerian-video-magnification-yolor-49818dd1b2f5#:~:text=Hao,tiniest%20motions%20and%20color%20changes)
[\[35\]](https://medium.com/augmented-startups/heart-rate-detection-using-eulerian-video-magnification-yolor-49818dd1b2f5#:~:text=them%20more%20obvious)
[\[36\]](https://medium.com/augmented-startups/heart-rate-detection-using-eulerian-video-magnification-yolor-49818dd1b2f5#:~:text=that%20there%20is%20a%20world,the%20help%20of%20some%20examples)
[\[37\]](https://medium.com/augmented-startups/heart-rate-detection-using-eulerian-video-magnification-yolor-49818dd1b2f5#:~:text=For%20example%2C%20there%20is%20a,heart%20rate%20of%20an%20individual)
[\[38\]](https://medium.com/augmented-startups/heart-rate-detection-using-eulerian-video-magnification-yolor-49818dd1b2f5#:~:text=In%20the%20GIF%20above%2C%20there,to%20be%20almost%20completely%20still)
[\[39\]](https://medium.com/augmented-startups/heart-rate-detection-using-eulerian-video-magnification-yolor-49818dd1b2f5#:~:text=to%20reveal%20the%20tiniest%20motions,and%20color%20changes)
Heart Rate Detection Using Eulerian Video Magnification & YOLOR \| by
Aditya Singh \| Augmented AI \| Medium

<https://medium.com/augmented-startups/heart-rate-detection-using-eulerian-video-magnification-yolor-49818dd1b2f5>

[\[40\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC6477570/#:~:text=Instant%20Stress%3A%20Detection%20of%20Perceived,physiological%20measurements%20for%20stress)
Instant Stress: Detection of Perceived Mental Stress Through \...

<https://pmc.ncbi.nlm.nih.gov/articles/PMC6477570/>

[\[41\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC10721846/#:~:text=,BVP%29%20signal%2C%20heart)
Challenges and prospects of visual contactless physiological \...

<https://pmc.ncbi.nlm.nih.gov/articles/PMC10721846/>

[\[42\]](https://www.researchgate.net/publication/357132971_Detecting_Human_Emotions_Through_Physiological_Signals_Using_Machine_Learning#:~:text=Detecting%20Human%20Emotions%20Through%20Physiological,the%20frame%20of%20the)
Detecting Human Emotions Through Physiological Signals Using \...

<https://www.researchgate.net/publication/357132971_Detecting_Human_Emotions_Through_Physiological_Signals_Using_Machine_Learning>

[\[43\]](https://www.mdpi.com/2072-4292/13/9/1785#:~:text=Integration%20of%20Visible%20and%20Thermal,the%20individual%20visible%20or)
Integration of Visible and Thermal Imagery with an Artificial Neural
\...

<https://www.mdpi.com/2072-4292/13/9/1785>
