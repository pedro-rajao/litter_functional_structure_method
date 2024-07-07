##########
Date: 05/01/2024
Author: Pedro Rajão 
Language: Python

##############################

Introduction
All leaves, branches, fruits and seeds of plants fall and accumulate on the forest floor in the form of litter (Sayer 2006). 
Litter performs multiple functions in ecosystems, from maintaining carbon sequestration in the soil, to the storage and progressive release of nutrients through decomposition, 
retention and dynamics of water in the soil, to dampening variations in soil temperature, in addition to the regeneration of trees and population and community dynamics of 
soil vegetation and fauna (Rajão et al. 2023, Felix et al. 2023, Dias et al. 2017, Seitz et al. 2015, Sato et al. 2004). 
In his review, Sayer (2006) summarized the evidence for the effect of litter structure on its multifunctionality through litter removal and addition experiments. 
From this, it was possible to establish that increasing litter cover increases moisture retention and reduces the impact of raindrops on the soil, protecting it against erosion, 
for example (Seitz et al. 2015, Sato et al. 2004). Additionally, Dias et al. (2017) summarized evidence for the role of species composition and functional traits (effect traits; Violle et al. 2007) of plant leaves 
in litter multifunctionality. Dias et al. (2017) revealed that “size and shape” and “economic” characteristics of leaves regulate the mechanisms behind litter 
multifunctionality (Grootemat et al. 2015, Cornelissen et al. 2017, Fuji et al. 2020, Rajão et al. 2023). For example, small leaves with a low specific leaf area (SLA) form more compact and spatially 
well-distributed litter, making it difficult to spread fire due to the difficulty in circulating oxygen (Grootemaat et al. 2015). However, most evidence about the effect of structure and functional composition on 
litter-mediated processes comes from small-scale experiments. Therefore, it is still necessary to advance studies in natural ecosystems, also monitoring the temporal dynamics of litter composition.
Both Sayer (2006) and Dias et al. (2017) assume that there is still a lot of empirical work ahead, mainly experiments in natural environments, to validate the role of litter structure and composition in litter 
multifunctionality. But, finding affordable tools to characterize and measure their cover and the composition of leaf size and shape (i.e. functional composition, aspects of functional identity and f
unctional diversity) has been a challenge for scientists and researchers. To achieve this, traditional methods require a large logistical and financial investment to carry out field campaigns, 
which involves the manipulation, collection, sorting and correct storage of litter or the use of probes and sensors (Rosalem et al. 2019, Sayer 2006). They are also generally destructive methods that 
generate changes in the environment that make studies on the temporal dynamics of litter multifunctionality difficult (Sayer 2006). As an alternative, we propose here a non-destructive approach using 
segmentation models to estimate leaf litter structure and characteristics parameters from photos. Advances in Artificial Intelligence (AI) in image processing have revolutionized the monitoring of 
environmental changes, disaster management and planning of urban areas (Osco et al. 2023REF). A critical part of image processing is the ability to accurately identify and segment multiple objects or 
regions within those images, a process known as segmentation. Segmentation allows us to isolate specific objects or areas within an image for study (Zhang et al. 2023) (Kotaridis and Lazaridou, 2021). 
Traditional segmentation techniques generally require a lot of operational effort to obtain accurate results. 
However, computer vision approaches and deep learning models have achieved excellent performances during image segmentation and processing (Bai et al., 2022, Aleissaee et al., 2023). 
Currently, many types and models of AI have stood out, and in this context, the Segment Anything Model (SAM), developed by Meta AI, brings an innovative approach demonstrating an exceptional 
generalization capacity, not requiring additional training for unknown objects and different shapes. and appearances (Kirillov et al., 2023). Recently, SAM has been tested in different uses and in
agricultural sciences to monitor crop plant growth, pest identification, and yield prediction (Williams et al. 2023). 
Here, we will be the first to use SAM to interpret forest properties under natural conditions in detecting and segmenting leaves from litter images.

To develop our method, we first tested SAM's ability to recognize leaves in an image and estimate their characteristics. Then, we check whether SAM results in leaf masks in images and is able to represent the 
functional composition of different litter compositions. Specifically, we tested the potential of masks to estimate the area (cm²), perimeter (cm) and area-to-perimeter ratio (cm².cm-¹) of leaves in litter in 
natural environments. 
Finally, we explored metrics that represent the structure and functional composition of the litter, such as leaf cover, mean and coefficient of variation, the latter representing a measure of functional diversity.
