# Chapter 2. Multi-Modal Physiological Data Collection Platform for Future GSR Prediction

## 2.1 Emotion Analysis Applications

Emotion recognition and stress monitoring have become vital in various
domains, leveraging physiological signals such as Galvanic Skin Response
(GSR) for insight into human states. GSR, in particular, is extensively
used in psychophysiological research; by the early 1970s over 1,500
scientific articles had been published on GSR, and it remains one of the
most popular methods for investigating human emotional
arousal[\[1\]](https://imotions.com/blog/learning/research-fundamentals/galvanic-skin-response/#:~:text=Top%20Applications%20of%20Galvanic%20Skin,Response%20in%20Research%20and%20Industry).
The broad applicability of GSR-driven emotion analysis includes diverse
fields:

- **Psychological and Clinical Research:** Psychologists use GSR to
  quantify emotional reactions to stimuli and to understand conditions
  like phobias or PTSD. Heightened GSR responses can indicate fear or
  stress in patients, and therapists monitor GSR during exposure or
  relaxation therapy to gauge treatment
  progress[\[2\]](https://imotions.com/blog/learning/research-fundamentals/galvanic-skin-response/#:~:text=Psychological%20Research%20Psychological%20studies%20utilize,with%20dogs%20in%20later%20life)[\[3\]](https://imotions.com/blog/learning/research-fundamentals/galvanic-skin-response/#:~:text=Clinical%20Research%C2%A0%26%20Psychotherapy%20Clinical%20populations,success%20of%20the%20therapeutic%20intervention).
  For example, a patient with anxiety might show elevated GSR when
  confronted with a feared stimulus, and a reduction over therapy
  sessions signals desensitization and recovery progress.
- **Marketing and Media Testing:** In consumer neuroscience and
  marketing, subtle differences in product appeal or advertisement
  impact can be objectively measured via GSR. Marketers track GSR to see
  which advertisements evoke arousal and engagement, identifying moments
  that resonate or fall
  flat[\[4\]](https://imotions.com/blog/learning/research-fundamentals/galvanic-skin-response/#:~:text=Consumer%C2%A0Neuroscience%20%26%C2%A0Marketing%20Evaluating%20consumer%20preferences,identify%20target%20audiences%20and%20personas)[\[5\]](https://imotions.com/blog/learning/research-fundamentals/galvanic-skin-response/#:~:text=Media%20%26%20Ad%C2%A0Testing%20In%20media,utilizing%20GSR%20for%20evaluation%20purposes).
  Similarly, media producers test audience responses to scenes in films
  or games; spikes in GSR can reveal excitement or stress at key
  moments, informing creative decisions.
- **Human--Computer Interaction and UX:** GSR is applied in usability
  studies to detect user frustration or cognitive load. When a user
  struggles with a confusing interface or encounters an error, their
  stress level rises, reflected in increased skin
  conductance[\[6\]](https://imotions.com/blog/learning/research-fundamentals/galvanic-skin-response/#:~:text=Usability%20Testing%C2%A0%26%20UX%20Design%20Using,in%20stereotypic%20GSR%20activation%20patterns).
  Designers leverage these insights to pinpoint problematic user
  interface elements. In adaptive systems, real-time GSR feedback can
  even trigger interface adjustments to reduce user stress, creating
  more responsive and empathetic technology.

These application areas underscore the importance of reliable emotional
state detection. They motivate the creation of robust data collection
platforms to fuel machine learning models that can recognize stress or
emotion. A multi-modal approach -- combining **physiological signals**
(like GSR) with **behavioral cues** (like facial expressions or thermal
signatures) -- promises richer data for these applications. The ultimate
goal is to enable models that can detect or predict stress accurately in
natural settings, which requires comprehensive, high-quality datasets.
By capturing synchronized multimodal data, the proposed platform aims to
provide the ground truth needed to train and validate such advanced
affective computing systems.

## 2.2 Rationale for Contactless Physiological Measurement

Traditional emotion detection often relies on wearable sensors (for
heart rate, skin conductance, etc.) attached to the user. While
effective, these contact-based methods can be obtrusive and may alter
the user's behavior or comfort. There is a strong rationale for
**contactless physiological measurement** techniques in stress and
emotion research. A contactless approach allows data to be gathered
without encumbering the subject, enabling more natural interactions and
broader applicability (e.g. in scenarios where wearing sensors is
impractical). For instance, in automotive research, monitoring driver
stress with cameras is preferable to wiring the driver with electrodes.
A recent study demonstrated a non-invasive driver stress monitoring
system using only thermal infrared imaging, validating its output
against traditional ECG-based stress
indices[\[7\]](https://www.mdpi.com/2076-3417/10/16/5673#:~:text=played%20by%20stress%20which%20can,linear).
The ability to assess stress state through a camera, without any
physical contact, was shown to be feasible and accurate, which is
promising for real-world driver assistance systems.

Contactless measurement is also advantageous for continuous mental
health monitoring in daily life. Modern smartphones equipped with
optical and thermal sensors can passively gauge physiological signals.
Researchers have combined smartphone camera photoplethysmography (for
heart pulse) with a small thermal camera to quickly detect stress
responses, aiming for quick and convenient daily
measurements[\[8\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC6477570/#:~:text=Recent%20studies%20have%20demonstrated%20that,Smartphone%20apps%20with%20such).
Such systems highlight that cameras (both regular RGB and infrared) can
capture proxies for vital signs -- for example, subtle changes in facial
blood flow or temperature -- without any attachments on the body. This
**unobtrusiveness** reduces the burden on participants and makes
long-term stress tracking more acceptable and scalable.

Given these benefits, our platform prioritizes contactless modalities
alongside traditional sensors. By integrating a thermal camera and
optionally the device's own RGB camera, we obtain physiological data
(like heat patterns or heart-rate-related signals) without additional
contact points beyond a simple finger GSR sensor. This approach supports
data collection in more natural environments (e.g. workplace, driving,
or everyday settings) where people might not tolerate multiple wired
sensors. In summary, the rationale for including contactless measurement
in a multimodal platform is to broaden the contexts in which
**high-quality stress data** can be collected, ensuring the platform can
be used comfortably and extensibly for future real-world **stress
inference** applications.

## 2.3 Definitions of "Stress" (Scientific vs. Colloquial)

The term "stress" carries distinct meanings in scientific literature
versus everyday conversation. **Scientifically**, stress is often
defined in terms of the body's physiological response to demands or
threats. Hans Selye's classic definition frames stress as "the
non-specific response of the body to any
demand"[\[9\]](https://healthylife.com/online/FullVersion/HealthHints/Chapter6_intro_HH.html#:~:text=Medicine%20healthylife,%E2%80%9D%20It%20does%20not).
In this view, any challenge -- whether physical or emotional -- triggers
a cascade of biological reactions (activation of the sympathetic nervous
system and the hypothalamic-pituitary-adrenal axis) that prepare the
organism to adapt. Scientific discussions of stress distinguish the
*stressor* (the challenging stimulus) from the *stress response* (the
body's reaction). Key aspects of the scientific concept include
measurable changes such as elevated adrenaline, **cortisol** secretion,
increased heart rate, and heightened GSR due to sympathetic
activation[\[10\]](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2020.00039/full#:~:text=It%20is%20generally%20accepted%20that,delay%20of%20about%2025%20min).
These are objectively observable indicators that an organism is under
strain. Notably, stress can be positive (eustress, which can enhance
performance) or negative (distress, which can be harmful), but in both
cases it involves a departure from homeostasis and activation of coping
mechanisms.

**Colloquially**, however, "stress" usually refers to a subjective
feeling of pressure, tension, or anxiety. In everyday usage, someone
saying "I feel stressed" typically means they are experiencing mental or
emotional strain. This informal definition aligns with descriptions like
that of the World Health Organization, which defines stress as a state
of worry or mental tension in response to a difficult
situation[\[11\]](https://www.who.int/news-room/questions-and-answers/item/stress#:~:text=Stress%20can%20be%20defined%20as,prompts%20us%20to%20address).
Colloquial stress is often used as an umbrella term encompassing both
the sources of stress ("I have a stressful job") and the feelings evoked
("I'm stressed out"). It may ignore the precise physiological
mechanisms, focusing instead on the perceived burden or discomfort. For
example, a tight deadline at work might be called "stressful" whether or
not it triggers significant biological stress responses, because the
individual *feels* under pressure.

In reconciling these definitions, it is important for our research to
clarify what aspect of "stress" we aim to measure. Our project is
concerned with **physiological stress responses** -- the objective
signals such as GSR changes, heart rate variability, and thermal
variations that accompany the stress state. These signals provide ground
truth data for building predictive models. However, we also acknowledge
that the **perception of stress** (as understood colloquially) is
relevant, since ultimately any automated GSR prediction system should
correlate with a person's experienced stress. By aligning scientific
measurements with everyday notions (e.g. validating that high GSR
coincides with self-reported stress levels), our platform and future
models can bridge the gap between the scientific and colloquial
understanding of stress.

## 2.4 Cortisol vs. GSR as Stress Indicators

**Cortisol** and **Galvanic Skin Response (GSR)** are both widely used
indicators of stress, but they represent very different physiological
pathways and timescales. Cortisol is a hormone released by the adrenal
cortex as the end product of the hypothalamic-pituitary-adrenal (HPA)
axis activation during stress. It is often regarded as a "gold-standard"
biochemical marker of stress, reflecting the body's hormonal stress
response. For instance, acute stressors (like the Trier Social Stress
Test) reliably cause a spike in cortisol about 20--30 minutes after the
stressful
event[\[10\]](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2020.00039/full#:~:text=It%20is%20generally%20accepted%20that,delay%20of%20about%2025%20min).
This delay occurs because cortisol release and distribution are
relatively slow processes: research confirms that psychological stress
triggers almost immediate sympathetic reactions, whereas cortisol peaks
only after a considerable
lag[\[12\]](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2020.00039/full#:~:text=In%20order%20to%20find%20a,completed%20stressful%2C%20boring%2C%20and%20performance).
Cortisol measurement (typically via saliva samples) thus provides a
*delayed* but specific index of stress level. High cortisol levels
indicate activation of the HPA axis, which is associated with sustained
stress and can have downstream effects on various organs and cognitive
functions.

In contrast, **GSR responds almost instantaneously to stress** via the
sympathetic nervous system. GSR (or electrodermal activity) is
controlled by sweat gland activity in the skin, which increases under
sympathetic drive. The moment an individual encounters a stressor --
e.g. a sudden scare or mental challenge -- their sympathetic nervous
system fires within seconds, causing heart rate and sweat secretion to
rise as part of the fight-or-flight
response[\[10\]](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2020.00039/full#:~:text=It%20is%20generally%20accepted%20that,delay%20of%20about%2025%20min).
As a result, skin conductance begins to climb almost immediately, often
within 1--3 seconds of a
stimulus[\[13\]](https://en.wikipedia.org/wiki/Electrodermal_activity#:~:text=example%2C%20the%20responses%20on%20the,38).
This makes GSR an excellent *real-time* indicator of arousal. For
example, during a stressful task, one can observe distinctive GSR peaks
corresponding to moments of heightened stress or excitement, long before
any cortisol changes would be
measurable[\[12\]](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2020.00039/full#:~:text=In%20order%20to%20find%20a,completed%20stressful%2C%20boring%2C%20and%20performance).
Because of this immediacy, GSR is invaluable for capturing the dynamic
pattern of stress responses on a second-by-second basis.

However, there are important distinctions and complementary aspects
between these two measures. **Cortisol** represents a downstream,
cumulative stress effect -- it reflects the intensity of stress exposure
over minutes and is relatively *specific* to true stress (since the HPA
axis is chiefly activated by stressors threatening enough to warrant a
hormonal response). It is less sensitive to brief, transient arousal
that might not be subjectively perceived as "stressful." **GSR**, on the
other hand, is a direct readout of sympathetic nervous system arousal.
It is extremely sensitive, registering any kind of emotional or physical
arousal (e.g. surprise, anxiety, excitement) even if those responses are
mild or
short-lived[\[14\]](https://en.wikipedia.org/wiki/Electrodermal_activity#:~:text=The%20traditional%20theory%20of%20EDA,although%20it%20is%20present%20in)[\[15\]](https://www.mdpi.com/2076-3417/14/24/11997#:~:text=devices%20is%20typically%20based%20on,2).
Thus, GSR can sometimes register false positives for "stress" (for
instance, excitement or startle responses produce GSR changes but might
not be considered stress in the colloquial sense). GSR is more of a
*situational marker* of arousal, while cortisol is a *hormonal marker*
of systemic stress
load[\[16\]](https://www.sciencedirect.com/science/article/pii/S136984782500244X#:~:text=,2019).

In our context of building a prediction platform, we primarily use GSR
as the **ground-truth stress signal** due to its high temporal
resolution and directness. The near-instantaneous changes in GSR allow
synchronization with other modalities (like video frames or thermal
readings) on a fine timescale. Cortisol, while not practical for
real-time data collection (given the need for sampling bodily fluids and
the latency of response), provides valuable scientific validation.
Indeed, one study modeled a *cortisol-equivalent stress indicator* from
GSR peaks and found significant correlation with measured salivary
cortisol[\[12\]](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2020.00039/full#:~:text=In%20order%20to%20find%20a,completed%20stressful%2C%20boring%2C%20and%20performance),
suggesting that carefully processed GSR data can approximate the
hormonal stress profile. This reinforces that GSR, despite its
limitations, is a powerful proxy for stress when collected properly. In
summary, cortisol and GSR each have roles: cortisol underscores the
biological significance of stress, whereas GSR offers an accessible,
immediate window into the sympathetic activation that accompanies
stress. Our platform leverages GSR as the primary stress indicator, with
the understanding that it captures the fast dynamics of stress responses
which future models will aim to predict.

## 2.5 GSR Physiology and Measurement Limitations

**Physiology of GSR:** Galvanic Skin Response is rooted in the activity
of eccrine sweat glands and the skin's electrical properties. When the
sympathetic branch of the autonomic nervous system is aroused (for
example, during stress or strong emotion), it drives the sweat
glands---particularly on the palms and soles---to produce
sweat[\[14\]](https://en.wikipedia.org/wiki/Electrodermal_activity#:~:text=The%20traditional%20theory%20of%20EDA,although%20it%20is%20present%20in).
Even imperceptible amounts of sweat in the skin change the skin's
conductivity (lowering its electrical resistance). GSR sensors typically
apply a tiny constant voltage across two skin contacts and measure the
conductance; an increase in conductance indicates greater sweat gland
activity and thus higher sympathetic
arousal[\[17\]](https://imotions.com/blog/learning/research-fundamentals/galvanic-skin-response/#:~:text=Logic%20Behind%20GSR%20Sensors).
This makes GSR a direct readout of physiological arousal levels. It is
**entirely involuntary** -- unlike facial expressions or heart rate, one
cannot consciously suppress or modulate their skin conductance. This is
why GSR is prized in psychophysiology: it offers an "honest" signal of
emotional arousal that is not under cognitive control. Numerous studies
and reviews acknowledge electrodermal activity as a primary indicator of
stress and
arousal[\[15\]](https://www.mdpi.com/2076-3417/14/24/11997#:~:text=devices%20is%20typically%20based%20on,2).
In summary, GSR's physiological basis (sweat secretion under sympathetic
control) ties it closely to the fight-or-flight machinery of the body,
which is exactly what we seek to monitor in stress research.

**Limitations of GSR measurements:** Despite its value, GSR is not a
perfect signal and comes with several important limitations and
challenges[\[18\]](https://en.wikipedia.org/wiki/Electrodermal_activity#:~:text=External%20factors%20such%20as%20temperature,not%20only%20with%20different%20sweat)[\[19\]](https://en.wikipedia.org/wiki/Electrodermal_activity#:~:text=measured%20in%20different%20places%20on,38):

- **Environmental and Individual Factors:** External conditions like
  ambient **temperature and humidity** can significantly affect skin
  conductance
  readings[\[18\]](https://en.wikipedia.org/wiki/Electrodermal_activity#:~:text=External%20factors%20such%20as%20temperature,not%20only%20with%20different%20sweat).
  Heat can increase baseline skin moisture, elevating GSR even without
  emotional stimuli, while cold dry air might suppress sweat response.
  Likewise, individual physiological factors -- such as a person's level
  of **hydration**, or if they are on certain **medications** (e.g.
  beta-blockers or SSRIs) -- can alter skin conductance
  responsiveness[\[18\]](https://en.wikipedia.org/wiki/Electrodermal_activity#:~:text=External%20factors%20such%20as%20temperature,not%20only%20with%20different%20sweat).
  This means the same stimulus might produce different GSR magnitudes in
  different conditions or people, reducing consistency. Proper
  experimental control or normalization is needed to account for these
  influences. Additionally, GSR can drift over time (skin becomes
  gradually sweatier or drier), so interpreting absolute values requires
  caution.
- **Sensor Placement and Response Variability:** The classic assumption
  is that GSR reflects a uniform "whole-body" arousal, but in reality it
  **varies by location**. Measurements on different body sites
  (fingertip, wrist, foot, etc.) can yield different response patterns,
  partly because different regions' sweat glands are regulated by
  different sympathetic
  nerves[\[20\]](https://en.wikipedia.org/wiki/Electrodermal_activity#:~:text=represented%20one%20homogeneous%20change%20in,relationship%20between%20EDA%20and%20sympathetic).
  For example, the left and right hands can show non-identical GSR
  responses to the same
  stimulus[\[21\]](https://en.wikipedia.org/wiki/Electrodermal_activity#:~:text=represented%20one%20homogeneous%20change%20in,not%20only%20with%20different%20sweat).
  This spatial variability means placement of electrodes must be chosen
  carefully (fingers are standard due to high sweat gland density and
  responsiveness). Moreover, GSR changes do not happen instantaneously;
  there is an inherent **lag of about 1--3 seconds** between a stimulus
  (e.g. a sudden stressor) and the rise of the GSR
  signal[\[19\]](https://en.wikipedia.org/wiki/Electrodermal_activity#:~:text=measured%20in%20different%20places%20on,38).
  This delay, due to physiological and electrochemical processes in the
  skin, complicates precise alignment with fast events. It requires any
  data collection platform to synchronize stimulus/event timestamps with
  GSR data while accounting for this latency. Finally, obtaining
  high-quality GSR data can depend on the **skill of the
  operator**[\[22\]](https://en.wikipedia.org/wiki/Electrodermal_activity#:~:text=Lastly%2C%20electrodermal%20responses%20are%20delayed,38)
  -- proper skin preparation, electrode attachment, and calibration are
  needed to avoid motion artifacts or poor contact, which can introduce
  noise.

These limitations underscore why a **multimodal approach** is
beneficial. By combining GSR with other signals (such as heart rate or
thermal imaging), we can cross-validate and compensate for cases when
GSR alone might be ambiguous or affected by external factors. In our
platform, careful attention is given to data quality: we use high-grade
GSR sensors (for stable readings), ensure consistent placement (finger
straps on the same hand for all sessions), and log environmental
conditions if necessary. We also design the data acquisition with
synchronization and timing in mind, so the known GSR lag can be
corrected in analysis. Recognizing GSR's limitations allows us to design
a collection system -- and later, predictive models -- that are more
robust and interpretable. GSR will serve as a core ground truth for
"stress" in the dataset, but it will be interpreted in context with the
other modalities to build a reliable inference model.

## 2.6 Thermal Cues of Stress in Humans

Beyond electrical signals like GSR, **thermal imaging** offers a
contactless window into physiological changes under stress. When a
person experiences stress, the autonomic nervous system not only
triggers sweating but also redistributes blood flow as part of the
fight-or-flight response. One observable consequence is peripheral
**vasoconstriction** -- blood vessels in the face and extremities may
constrict, leading to cooler skin temperatures in those regions. Thermal
cameras can detect these subtle temperature shifts. Research has
consistently found that acute stress or fear is accompanied by a
measurable drop in temperature at the tip of the nose and across parts
of the
face[\[23\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=reflected%20by%20a%20drop%20in,cheeks%2C%20chin%2C%20periorbital%2C%20and%20maxillary).
For example, in controlled studies where participants underwent a stress
task (like the Stroop test or public speaking), infrared thermal cameras
recorded that the participants' nose tip temperature decreased
significantly during stress, then rebounded as they
recovered[\[24\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=during%20the%20Stroop%20session,during%20the%20Stroop%20compared%20to)[\[23\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=reflected%20by%20a%20drop%20in,cheeks%2C%20chin%2C%20periorbital%2C%20and%20maxillary).
This "cold nose" effect is considered a hallmark thermal signature of
stress and is attributed to sympathetic vasoconstriction diverting blood
to core organs.

In addition to cooling effects, thermal imaging can capture signs of
**stress-induced perspiration** and related heat dissipation. A
prominent finding by Pavlidis et al. is that stress activates sweat
glands especially in the **periorbital (around the eyes) and nasal
regions**, leading to increased evaporation and cooling that a thermal
camera can pick up as temperature
fluctuations[\[25\]](https://www.mdpi.com/2076-3417/10/16/5673#:~:text=test%20%28r%20%3D%200,The).
Their system, often dubbed a "StressCam," showed that the heat patterns
on the face -- particularly the warming from blood flow and the cooling
from evaporative sweat -- correlate strongly with psychological stress
levels[\[25\]](https://www.mdpi.com/2076-3417/10/16/5673#:~:text=test%20%28r%20%3D%200,The).
For instance, during a sudden stress event, one might observe a
transient warming in the forehead (from a quick blood pressure rise) but
a cooling around the nose and mouth (from evaporative cooling of sweat).
These patterns are **sympathetically driven**, meaning they stem from
the same nervous activation that causes GSR
changes[\[26\]](https://www.mdpi.com/2076-3417/10/16/5673#:~:text=test%20%28r%20%3D%200,The).
Thus, they provide a complementary view of the stress response. Thermal
cues have been used to detect concealed stress or even deceit; a
well-known application is lie detection, where a thermal camera can spot
the "heat signature" of stress around the eyes (from blood vessel
dilation) or the cooling of the nose when a person is under the anxiety
of lying.

Recent advances in higher-resolution thermal imaging and computer vision
have expanded the analysis to multiple facial regions. Rather than
relying only on the nose tip, researchers define regions of interest
(ROIs) across the face (forehead, cheeks, nose, periorbital area, etc.)
and track how each ROI's temperature changes under
stress[\[27\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=nose%20tip%2C%20forehead%20,is%20represented%20in%20Figure%202)[\[23\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=reflected%20by%20a%20drop%20in,cheeks%2C%20chin%2C%20periorbital%2C%20and%20maxillary).
This approach has revealed a complex picture: for instance, one study
noted that during a cognitive stress task, not only did nose and
periorbital regions cool, but the cheeks actually showed a slight
increase in temperature (perhaps due to blushing or muscle
activity)[\[24\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=during%20the%20Stroop%20session,during%20the%20Stroop%20compared%20to).
Such findings suggest that a multi-region thermal analysis can yield a
rich feature set for machine learning -- essentially a "thermal
signature" of stress encompassing several physiological processes.

For our platform, the inclusion of a thermal camera is driven by these
known thermal cues of stress. By recording thermal video of a
participant's face or hands during data collection, we capture signals
like nose-tip cooling and perinasal perspiration remotely, in sync with
GSR. These thermal features will serve as valuable predictors for stress
in future models. Importantly, they are **contactless** and
non-invasive, aligning with our rationale (Section 2.2) to make the data
collection as natural as possible. Thermal imaging thereby provides a
bridge between purely internal signals (like GSR or cortisol) and
external observations -- it visualizes the autonomic changes on the
surface of the skin, giving our multimodal dataset another dimension of
ground truth for stress that can be leveraged by machine learning
algorithms.

## 2.7 RGB vs. Thermal Imaging (Machine Learning Hypothesis)

In designing a multimodal platform for stress data, we consider both
**visible spectrum (RGB) imaging** and **thermal infrared imaging** as
complementary modalities. Each type of camera offers unique information:
an RGB camera (like a standard smartphone camera) captures fine details
of facial expression, skin color changes, and movements, while a thermal
camera captures the invisible heat patterns related to blood flow and
sweat. A central hypothesis for future **machine learning** models is
that combining RGB and thermal data will yield more accurate and robust
predictions of stress (or GSR levels) than either modality alone. This
is grounded in the idea that stress manifests in multiple observable
ways -- some best seen in the visible domain (e.g. a furrowed brow, a
pale face due to reduced blood flow, or subtle tremors), and others only
detectable thermally (e.g. temperature drop on the skin, increased heat
from breath or perspiration). By fusing these, an AI model can develop a
holistic picture of the person's state.

Prior work supports this multimodal advantage. For instance, researchers
have built **dual-camera systems** that pair a regular camera with a
thermal sensor and found that the combination dramatically increases the
richness of physiological measurements
available[\[28\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC6477570/#:~:text=results%20suggest%20that%20smartphones%20could,There%20is%20also%20a%20strong).
A smartphone-based study reported that an integrated approach (using the
phone's camera for imaging blood volume pulse and an attached thermal
camera for nose-tip temperature) could quickly detect stress and
produced better classification accuracy than single
sensors[\[29\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC6477570/#:~:text=Recent%20studies%20have%20demonstrated%20that,possible%20tools%20for%20facilitating%20stress)[\[30\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC6477570/#:~:text=very%20dependent%20upon%20one%20another,Our%20results%20showed%20the).
In that study, using both modalities improved stress inference accuracy
to \~78%, compared to \~68% using only the photoplethysmography
(RGB-based) data or \~59% using only thermal
data[\[30\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC6477570/#:~:text=very%20dependent%20upon%20one%20another,Our%20results%20showed%20the).
This demonstrates **synergy**: the errors of one modality may be
compensated by the other. For example, if visible facial cues are
ambiguous (person maintains a neutral expression), thermal cues might
still reveal physiological stress, and vice versa (if a thermal signal
is unclear due to an external heat source, the RGB camera might capture
a telltale anxious fidget or change in complexion).

From a machine learning perspective, RGB and thermal images together
provide a multi-channel input that can enable more robust feature
extraction. **RGB video** frames can be processed to extract heart rate
(via subtle color changes in the face), breathing rate (via chest
movements), and facial action units (muscle movements indicating
emotion). **Thermal video** frames can be processed to extract
temperature-based features like the nose-facial temperature gradient,
rate of thermal change, or the presence of cool spots from sweating. Our
hypothesis is that a model trained on a well-synchronized dataset of
both types of data alongside ground-truth GSR will learn latent patterns
that correlate with stress more strongly than either alone. For
instance, a sudden stress event might cause a combination of cues: a
facial expression change (widened eyes) and a thermal drop in nose
temperature. A multimodal model could learn this joint signature whereas
a unimodal model might catch only one and be less certain.

To facilitate this, our data collection platform is designed to record
**synchronized RGB and thermal streams**. By capturing both, we ensure
that for every moment in time, we have aligned data: a thermal image and
a corresponding RGB image (and of course the physiological readings like
GSR). This alignment is crucial for training algorithms to exploit
cross-modal features. It also allows us to test the hypothesis: we can
train machine learning models on just RGB data, just thermal data, and
the combination, to quantitatively evaluate the benefit of multi-modal
integration. Based on the literature and our understanding, we
anticipate the fused model will outperform because the RGB vs. Thermal
modalities are not redundant but rather complementary. Ultimately, this
approach aims to pave the way for **contactless stress inference**: if a
model can reliably predict GSR (or stress levels) from just cameras, it
could enable real-time stress monitoring using everyday devices. Thus,
Section 2.7 underlines the theoretical foundation for including both
imaging modalities in the platform and guides our plan for future
machine learning experiments using the collected dataset.

## 2.8 Sensor Device Selection Rationale (Shimmer GSR Sensor and Topdon Thermal Camera)

To realize the above goals, we carefully chose the hardware components
for our multimodal data collection platform. The selection of sensors
was based on their signal quality, compatibility, and ability to provide
**synchronized, high-resolution data**. The platform's current
configuration centers on two primary devices: the **Shimmer 3 GSR+
sensor** for electrodermal activity and the **Topdon TC001 thermal
camera** for infrared imaging. We detail the rationale for each:

- **Shimmer 3 GSR+ (Galvanic Skin Response sensor):** The Shimmer GSR
  unit is a research-grade wearable sensor widely used in academic and
  clinical studies for EDA/GSR measurement. We selected Shimmer over
  consumer fitness devices (like smartwatches) to ensure **data accuracy
  and flexibility**. The Shimmer 3 GSR+ provides raw skin conductance
  data with high resolution and sampling rates (up to 128
  Hz)[\[31\]](https://www.mdpi.com/2076-3417/14/24/11997#:~:text=Shimmer%20device%2C%20attached%20to%20the,time%20via%20Bluetooth%20to%20a),
  far exceeding the 4--10 Hz sampling typical of wristband trackers.
  This high sampling rate means we capture the fast phasic changes in
  GSR without aliasing, which is crucial for precise synchronization
  with video frames. Moreover, Shimmer's reliability has been
  demonstrated in comparative evaluations -- studies comparing the
  Shimmer GSR sensor to popular devices (e.g., Empatica E4 wristband or
  Fitbit Sense) found Shimmer data to be consistently robust and
  trustworthy for stress
  research[\[32\]](https://www.mdpi.com/2076-3417/14/24/11997#:~:text=future%20research,world%20applications).
  The sensor uses Ag/AgCl electrodes attached to the fingers, providing
  a low-noise conductance measurement and it interfaces via Bluetooth,
  streaming data in real-time for synchronization. The Shimmer was also
  chosen for its **extensibility**: it includes additional channels
  (like a photoplethysmograph/PPG and accelerometer), which we can
  utilize to collect heart rate or motion data in the future without
  adding another
  device[\[33\]](https://www.mdpi.com/2076-3417/14/24/11997#:~:text=Measurements%20were%20performed%20using%20Shimmer,to%20assess%20the%20galvanic%20skin).
  The decision to use Shimmer ensures that our "ground truth" GSR signal
  is of the highest possible quality, serving as a dependable reference
  for training machine learning models.

- **Topdon TC001 Thermal Camera (USB, Android-compatible):** For the
  thermal imaging component, we required a camera that is **portable**,
  offers **high infrared resolution**, and can integrate with a mobile
  platform for synchronized recording. The Topdon TC001 thermal camera
  was selected after evaluating several thermal imaging options. It
  features an **IR sensor resolution of 256×192 pixels** (which can be
  enhanced via image processing to an equivalent 512×384
  resolution)[\[34\]](https://www.topdon.us/products/tc001?srsltid=AfmBOorvPZK1gCmPWxofEW4kOqMsaBmOdKYBo3ynu2i2Awvug-a_twE4#:~:text=TC001%20,The%20TC001%20is%20especially),
  substantially higher than many consumer thermal cameras (for
  comparison, the popular FLIR One Pro has a native 160×120 resolution).
  This higher pixel count allows finer discrimination of small
  temperature differences on the face or skin, improving the fidelity of
  stress-related thermal features. The TC001 is designed to connect
  directly to an Android smartphone via USB-C, essentially turning the
  phone into a thermal camera display and recorder. This plug-and-play
  compatibility was a major reason for our choice -- it allowed us to
  integrate the thermal feed into our **Android-based data collection
  app** with relative ease. The camera comes with an open SDK and uses
  standard UVC (USB Video Class) protocols, meaning we can
  programmatically control it and capture frames in sync with other
  sensors. Additionally, the Topdon camera operates at a decent frame
  rate (up to \~25--30 frames per second), enabling us to capture fluid
  thermal video of physiological changes. We also considered the
  device's **calibration and accuracy**: the TC001 has an optimized
  temperature accuracy and includes a calibration shutter, which helps
  maintain accurate absolute temperature readings across sessions
  (useful if we need actual temperature values for analysis, not just
  relative changes). Practically speaking, the Topdon offered the best
  trade-off between cost and performance for our academic project -- it
  is more affordable than high-end FLIR cameras but still delivers
  high-quality data. By using this camera, we ensure that our platform's
  thermal channel is rich enough for detailed analysis of stress
  patterns (like those discussed in Section 2.6).

**Synchronization and Integration:** A critical aspect of using these
devices together is achieving precise time alignment. The Shimmer GSR
sensor provides timestamps for each data point and the Android device
hosting the thermal camera can timestamp each frame; we implemented a
synchronization mechanism (a master clock in the recording app) to align
the streams. This way, we can correlate each GSR peak with the exact
thermal image frames (and any RGB frames, if using the phone camera)
around that moment. The importance of synchronization cannot be
overstated -- misaligned data could lead to incorrect labeling (e.g.,
attributing a GSR surge to the wrong facial expression). Our platform
uses a **common time base** and logging system to ensure all modalities
(GSR, thermal, and any others) are recorded in lockstep. Early
development included calibration routines where we trigger known events
(like a LED flash visible in both thermal and RGB, or a manual signal
causing a GSR spike) to measure and correct any offsets between sensors.

**Extensibility:** The chosen sensor set is meant to be extensible. The
**Android smartphone** that acts as the hub can also record **RGB
video** from its built-in camera simultaneously, adding an additional
modality (this was discussed in Section 2.7). We can enable or disable
this as needed. The hardware and software design allows adding further
sensors such as a heart rate chest strap or a respiration belt, as long
as they can interface via Bluetooth or USB to the same system -- future
researchers or developers can plug in new data streams and have them
synchronized with the existing ones. The Shimmer's modular nature (it
can be fitted with other sensing modules like ECG or EMG) and the
Android platform's connectivity mean the **multi-modal platform can
grow** to incorporate new physiological signals or environmental sensors
with minimal changes. This extensibility supports our central
motivation: to create a **synchronized, high-quality multimodal
dataset** that is *future-proof* for various machine learning modeling
efforts. Whether the goal is to predict GSR from thermal images, to
classify stress vs. no-stress from all modalities, or to explore new
physiological correlations, the platform provides a flexible foundation.

In conclusion, the combination of the Shimmer GSR sensor and the Topdon
thermal camera was deliberate to ensure we capture **ground-truth stress
signals (GSR) alongside rich, contactless indicators (thermal
imagery)**. By using research-grade and high-resolution devices, we
maximize data quality. By focusing on synchronization and extensibility,
we ensure the data is **machine-learning ready** -- correctly aligned
and scalable. Every section in this chapter has underscored that our aim
is not real-time inference for its own sake, but rather the **collection
of robust, ground-truth aligned multimodal data**. The rationale behind
each component choice is ultimately to serve that aim, yielding a
platform capable of underpinning advanced GSR prediction models in the
future. The next steps will involve deploying this platform in
experimental settings, collecting a comprehensive dataset, and then
utilizing it to train and evaluate the machine learning models that
motivated its creation.

------------------------------------------------------------------------

[\[1\]](https://imotions.com/blog/learning/research-fundamentals/galvanic-skin-response/#:~:text=Top%20Applications%20of%20Galvanic%20Skin,Response%20in%20Research%20and%20Industry)
[\[2\]](https://imotions.com/blog/learning/research-fundamentals/galvanic-skin-response/#:~:text=Psychological%20Research%20Psychological%20studies%20utilize,with%20dogs%20in%20later%20life)
[\[3\]](https://imotions.com/blog/learning/research-fundamentals/galvanic-skin-response/#:~:text=Clinical%20Research%C2%A0%26%20Psychotherapy%20Clinical%20populations,success%20of%20the%20therapeutic%20intervention)
[\[4\]](https://imotions.com/blog/learning/research-fundamentals/galvanic-skin-response/#:~:text=Consumer%C2%A0Neuroscience%20%26%C2%A0Marketing%20Evaluating%20consumer%20preferences,identify%20target%20audiences%20and%20personas)
[\[5\]](https://imotions.com/blog/learning/research-fundamentals/galvanic-skin-response/#:~:text=Media%20%26%20Ad%C2%A0Testing%20In%20media,utilizing%20GSR%20for%20evaluation%20purposes)
[\[6\]](https://imotions.com/blog/learning/research-fundamentals/galvanic-skin-response/#:~:text=Usability%20Testing%C2%A0%26%20UX%20Design%20Using,in%20stereotypic%20GSR%20activation%20patterns)
[\[17\]](https://imotions.com/blog/learning/research-fundamentals/galvanic-skin-response/#:~:text=Logic%20Behind%20GSR%20Sensors)
Galvanic Skin Response (GSR): The Complete Pocket Guide - iMotions

<https://imotions.com/blog/learning/research-fundamentals/galvanic-skin-response/>

[\[7\]](https://www.mdpi.com/2076-3417/10/16/5673#:~:text=played%20by%20stress%20which%20can,linear)
[\[25\]](https://www.mdpi.com/2076-3417/10/16/5673#:~:text=test%20%28r%20%3D%200,The)
[\[26\]](https://www.mdpi.com/2076-3417/10/16/5673#:~:text=test%20%28r%20%3D%200,The)
Driver Stress State Evaluation by Means of Thermal Imaging: A Supervised
Machine Learning Approach Based on ECG Signal

<https://www.mdpi.com/2076-3417/10/16/5673>

[\[8\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC6477570/#:~:text=Recent%20studies%20have%20demonstrated%20that,Smartphone%20apps%20with%20such)
[\[28\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC6477570/#:~:text=results%20suggest%20that%20smartphones%20could,There%20is%20also%20a%20strong)
[\[29\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC6477570/#:~:text=Recent%20studies%20have%20demonstrated%20that,possible%20tools%20for%20facilitating%20stress)
[\[30\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC6477570/#:~:text=very%20dependent%20upon%20one%20another,Our%20results%20showed%20the)
Instant Stress: Detection of Perceived Mental Stress Through Smartphone
Photoplethysmography and Thermal Imaging - PMC

<https://pmc.ncbi.nlm.nih.gov/articles/PMC6477570/>

[\[9\]](https://healthylife.com/online/FullVersion/HealthHints/Chapter6_intro_HH.html#:~:text=Medicine%20healthylife,%E2%80%9D%20It%20does%20not)
Chapter6_intro_HH - American Institute for Preventive Medicine

<https://healthylife.com/online/FullVersion/HealthHints/Chapter6_intro_HH.html>

[\[10\]](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2020.00039/full#:~:text=It%20is%20generally%20accepted%20that,delay%20of%20about%2025%20min)
[\[12\]](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2020.00039/full#:~:text=In%20order%20to%20find%20a,completed%20stressful%2C%20boring%2C%20and%20performance)
Frontiers \| Deriving a Cortisol-Related Stress Indicator From Wearable
Skin Conductance Measurements: Quantitative Model & Experimental
Validation

<https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2020.00039/full>

[\[11\]](https://www.who.int/news-room/questions-and-answers/item/stress#:~:text=Stress%20can%20be%20defined%20as,prompts%20us%20to%20address)
Stress - World Health Organization (WHO)

<https://www.who.int/news-room/questions-and-answers/item/stress>

[\[13\]](https://en.wikipedia.org/wiki/Electrodermal_activity#:~:text=example%2C%20the%20responses%20on%20the,38)
[\[14\]](https://en.wikipedia.org/wiki/Electrodermal_activity#:~:text=The%20traditional%20theory%20of%20EDA,although%20it%20is%20present%20in)
[\[18\]](https://en.wikipedia.org/wiki/Electrodermal_activity#:~:text=External%20factors%20such%20as%20temperature,not%20only%20with%20different%20sweat)
[\[19\]](https://en.wikipedia.org/wiki/Electrodermal_activity#:~:text=measured%20in%20different%20places%20on,38)
[\[20\]](https://en.wikipedia.org/wiki/Electrodermal_activity#:~:text=represented%20one%20homogeneous%20change%20in,relationship%20between%20EDA%20and%20sympathetic)
[\[21\]](https://en.wikipedia.org/wiki/Electrodermal_activity#:~:text=represented%20one%20homogeneous%20change%20in,not%20only%20with%20different%20sweat)
[\[22\]](https://en.wikipedia.org/wiki/Electrodermal_activity#:~:text=Lastly%2C%20electrodermal%20responses%20are%20delayed,38)
Electrodermal activity - Wikipedia

<https://en.wikipedia.org/wiki/Electrodermal_activity>

[\[15\]](https://www.mdpi.com/2076-3417/14/24/11997#:~:text=devices%20is%20typically%20based%20on,2)
[\[31\]](https://www.mdpi.com/2076-3417/14/24/11997#:~:text=Shimmer%20device%2C%20attached%20to%20the,time%20via%20Bluetooth%20to%20a)
[\[32\]](https://www.mdpi.com/2076-3417/14/24/11997#:~:text=future%20research,world%20applications)
[\[33\]](https://www.mdpi.com/2076-3417/14/24/11997#:~:text=Measurements%20were%20performed%20using%20Shimmer,to%20assess%20the%20galvanic%20skin)
Galvanic Skin Response and Photoplethysmography for Stress Recognition
Using Machine Learning and Wearable Sensors

<https://www.mdpi.com/2076-3417/14/24/11997>

[\[16\]](https://www.sciencedirect.com/science/article/pii/S136984782500244X#:~:text=,2019)
Investigating simulator validity by using physiological and cognitive
\...

<https://www.sciencedirect.com/science/article/pii/S136984782500244X>

[\[23\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=reflected%20by%20a%20drop%20in,cheeks%2C%20chin%2C%20periorbital%2C%20and%20maxillary)
[\[24\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=during%20the%20Stroop%20session,during%20the%20Stroop%20compared%20to)
[\[27\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=nose%20tip%2C%20forehead%20,is%20represented%20in%20Figure%202)
Towards a Contactless Stress Classification Using Thermal Imaging

<https://www.mdpi.com/1424-8220/22/3/976>

[\[34\]](https://www.topdon.us/products/tc001?srsltid=AfmBOorvPZK1gCmPWxofEW4kOqMsaBmOdKYBo3ynu2i2Awvug-a_twE4#:~:text=TC001%20,The%20TC001%20is%20especially)
TC001 (Android Devices) -- TOPDON USA

<https://www.topdon.us/products/tc001?srsltid=AfmBOorvPZK1gCmPWxofEW4kOqMsaBmOdKYBo3ynu2i2Awvug-a_twE4>
