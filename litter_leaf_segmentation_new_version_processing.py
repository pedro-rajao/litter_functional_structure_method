# -*- coding: utf-8 -*-
"""litter_leaf_segmentation_NEW_VERSION_processing

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1fanW6TX9TyC2DYGryZoAg7XFcC-ejAcg
"""

# Commented out IPython magic to ensure Python compatibility.
# Clear GPU memory cache and close all active CUDA contexts
import torch
torch.cuda.empty_cache()
import cv2
from matplotlib import pyplot as plt
from google.colab import files

#########################
##### model SAM
####################

## models adjustment, weights and data
import os
HOME = os.getcwd()
print("HOME:", HOME)
# %cd {HOME}
import sys
!{sys.executable} -m pip install 'git+https://github.com/facebookresearch/segment-anything.git'
!pip install -q jupyter_bbox_widget roboflow dataclasses-json supervision
# %cd {HOME}
!mkdir {HOME}/weights
# %cd {HOME}/weights
!wget -q https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth
import os
CHECKPOINT_PATH = os.path.join(HOME, "weights", "sam_vit_h_4b8939.pth")
import torch
DEVICE = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
MODEL_TYPE = "vit_h"
!pip install --upgrade Pillow

###################
#### SAM
###########

from segment_anything import sam_model_registry, SamAutomaticMaskGenerator, SamPredictor
sam = sam_model_registry[MODEL_TYPE](checkpoint=CHECKPOINT_PATH).to(device=DEVICE)
mask_generator = SamAutomaticMaskGenerator(sam)

# Function to handle file upload
def handle_image_upload(upload_widget, selected_image_name):
    _file = upload_widget[selected_image_name]
    with open(selected_image_name, 'wb') as f:
        f.write(_file['content'])
    return selected_image_name

# Use file upload widget to select an image
print("Please select an image to process:")
upload_widget = files.upload()

###############
#### plots masks
###########
!pip install cv2
torch.cuda.empty_cache()

import cv2
# Caminho da imagem de entrada
caminho_imagem = '68229-ser.jpg'
# Carregar a imagem usando OpenCV
image_bgr = cv2.imread(caminho_imagem)
image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
altura, largura, _ = image_rgb.shape
fator_escala = 0.4
nova_largura = int(largura * fator_escala)
nova_altura = int(altura * fator_escala)
imagem_redimensionada = cv2.resize(image_rgb, (nova_largura, nova_altura))
imagem_plot = imagem_redimensionada.copy()
sam_result = mask_generator.generate(imagem_redimensionada)

!pip install supervision
import supervision as sv
mask_annotator = sv.MaskAnnotator(color_lookup=sv.ColorLookup.INDEX)
detections = sv.Detections.from_sam(sam_result=sam_result)
annotated_image = mask_annotator.annotate(imagem_redimensionada, detections)

masks = [
    mask['segmentation']
    for mask
    in sorted(sam_result, key=lambda x: x['area'], reverse=True)
]

# analisa as máscaras
import numpy as np
areas = [np.count_nonzero(mask) for mask in masks]
print(f"Área Mínima das Máscaras: {min(areas)} pixels")
print(f"Área Máxima das Máscaras: {max(areas)} pixels")

import random
num_masks_to_visualize = 16
indices_masks_to_visualize = random.sample(range(len(masks)), num_masks_to_visualize)

# Sort the masks by area in ascending order (smallest to largest)
masks_filtradas_sorted = sorted(masks, key=lambda x: np.count_nonzero(x))

smallest_mask = masks_filtradas_sorted[0]
largest_mask = masks_filtradas_sorted[-1]
smallest_mask_array = np.array(smallest_mask, dtype=np.uint8)
largest_mask_array = np.array(largest_mask, dtype=np.uint8)


# Create a figure and two subplots to display the masks
from matplotlib import pyplot as plt
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
ax1.imshow(smallest_mask_array, cmap='gray')
ax1.set_title('Smallest Mask')
ax2.imshow(largest_mask_array, cmap='gray')
ax2.set_title('Largest Mask')

plt.show()


# plota 16 MASCARAS ALEATORIAS
plt.figure(figsize=(12, 12))
for i, index in enumerate(indices_masks_to_visualize):
    mask = masks[index]
    plt.subplot(4, 4, i + 1)  # Cria um subplot de 4x4
    plt.imshow(mask, cmap='gray')  # Exibe a máscara em escala de cinza
    plt.title(f'mascara {index}', fontsize=12)  # Define o título com a posição na lista

plt.tight_layout()
plt.show()  # Exibe as máscaras aleatoriamente

shape_of_mask = detections.mask.shape
print("Shape of the mask array:", shape_of_mask)

masks_filtradas = [mask for mask in sam_result if mask['area'] >= 100]

masks_filtradas_sorted = sorted(masks_filtradas, key=lambda x: x['area'])

import matplotlib.pyplot as plt
# Plot the image
plt.figure(figsize=(8, 8))  # Set the figure size as desired
plt.imshow(imagem_plot)
plt.title('Annotated Image')
plt.axis('off')  # Turn off axis numbers and labels
plt.show()

binary_mask_array = detections.mask.astype(np.uint8)

#########################
##### plots images and images-masks SAM

annotated_image_copy = annotated_image.copy()

indices_masks_filtradas = [index for index, mask in enumerate(sam_result) if mask['area'] >=1000]

for idx, mask in enumerate(binary_mask_array):
    binary_mask = np.where(mask> 0, 1, 0).astype(np.uint8)  # binarize the mask
    contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # find the contour
    if len(contours) > 0 and cv2.contourArea(contours[0]) > 0:
        M = cv2.moments(contours[0])
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])

        # Aumentar o tamanho da fonte
        font_scale = 1  # Defina o tamanho da fonte desejado
        font_color = (0, 255, 0)  # Cor da fonte (verde)
        font_thickness = 1  # Espessura da fonte

        cv2.putText(annotated_image_copy, str(idx), (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_color, font_thickness)


######## plots images
# plot larger images without resizing
plt.figure(figsize=(30, 20))

# plot the source image
plt.subplot(1, 3, 1)
plt.imshow(cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB))
plt.title('Source Image', fontsize=30)
plt.axis('off')

# Plot the SAM segmented image
plt.subplot(1, 3, 2)
plt.imshow(annotated_image)
plt.title('SAM Segmented Image', fontsize=30)
plt.axis('off')

# Plot the SAM segmented image with numbers
plt.subplot(1, 3, 3)
plt.imshow(annotated_image_copy)
plt.title('SAM Segmented Image with ID Masks', fontsize=30)
plt.axis('off')

plt.tight_layout()
plt.show()

binary_mask_array = detections.mask.astype(np.uint8)
binary_mask_array

import cv2
import numpy as np

# Assuming other parts of your code and variables (like masks_filtradas_sorted) are defined above

for idx, mask in enumerate(binary_mask_array):
    binary_mask = np.where(mask > 0, 1, 0).astype(np.uint8)  # Binarize the mask
    contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # Find the contour
    if len(contours) > 0 and cv2.contourArea(contours[0]) > 0:
        M = cv2.moments(contours[0])
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        cv2.putText(annotated_image_copy, str(idx), (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_color, font_thickness)

    # Save the binary mask
    mask_filename = f"mask_{idx}.png"  # Naming each mask file uniquely
    cv2.imwrite(mask_filename, binary_mask * 255)  # Multiply by 255 to convert 1's to 255 (white)

####################
### TIFF exportation

import cv2
import numpy as np
import tifffile

binary_masks = []

for idx, mask in enumerate(binary_mask_array):
    binary_mask = np.where(mask > 0, 1, 0).astype(np.uint8)  # Binarize the mask
    contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # Find the contour
    if len(contours) > 0 and cv2.contourArea(contours[0]) > 0:
        M = cv2.moments(contours[0])
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
    binary_masks.append(binary_mask * 255)  # Add the mask to the list

# Stack all binary masks into a single 3D array
mask_stack = np.stack(binary_masks, axis=0)

# Save the stack as a TIFF file
tifffile.imwrite('/content/masks_stack_68228.tif', mask_stack)

####################################
### MASKs inspection and correction!
import pandas as pd
masks_filtradas = [mask for mask in sam_result if mask['area'] >= 1000]

# Crie um novo DataFrame apenas com as máscaras filtradas
df = pd.DataFrame(masks_filtradas)
masks_to_keep = []
for i, row in df.iterrows():
    # Se o ponto de coordenada já estiver em uma máscara anterior, exclua esta máscara
    if not any(all(point in mask for point in row['point_coords']) for mask in df.loc[masks_to_keep, 'point_coords']):
        masks_to_keep.append(i)
masks_filtradas_V2 = df.loc[masks_to_keep].reset_index(drop=True)
((masks_filtradas_V2))
# comparando dataframes COM e SEM mascaras sobrepostas
num_linhas_masks_filtradas = len(masks_filtradas)
num_linhas_masks_filtradas_V2 = len(masks_filtradas_V2)
print("Número de linhas em masks_filtradas:", num_linhas_masks_filtradas)
print("Número de linhas em masks_filtradas_V2:", num_linhas_masks_filtradas_V2)

print(df)

import matplotlib.pyplot as plt
import cv2
import numpy as np

# Lista de cores para os contornos das máscaras
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255),
          (0, 255, 255), (128, 0, 0), (0, 128, 0), (0, 0, 128), (128, 128, 0)]

# Função para desenhar contorno com cor e texto com cor correspondente
def draw_contour_with_id(image, contour, idx, color):
    # Define a cor do contorno e do texto
    # Desenha o contorno
    cv2.drawContours(image, [contour], 0, color, 1)
    # Calcula o centro do contorno para posicionar o texto
    M = cv2.moments(contour)
    if M["m00"] != 0:
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        # Desenha o texto com a mesma cor do contorno
        cv2.putText(image, str(idx), (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

# Plot larger images without resizing
plt.figure(figsize=(20, 20))

# Plot the source image
plt.subplot(2, 2, 1)
plt.imshow(cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB))
plt.title('Source Image', fontsize=20)
plt.axis('off')

# Plot the SAM segmented image
plt.subplot(2, 2, 2)
plt.imshow(annotated_image)
plt.title('SAM Segmented Image', fontsize=20)
plt.axis('off')

# Plot the SAM segmented image with IDs without filter
plt.subplot(2, 2, 3)
annotated_image_copy = annotated_image.copy()
# Plot annotated_image_copy with IDs
for idx, mask in enumerate(masks_filtradas):
    binary_mask = np.array(mask['segmentation'], dtype=np.uint8)
    contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        draw_contour_with_id(annotated_image_copy, cnt, idx, (0, 255, 0))  # Cor verde para IDs

plt.imshow(annotated_image_copy)
plt.title('SAM Segmented Image with ID Masks without filter', fontsize=20)
plt.axis('off')

# Plot the original image with masks and IDs
plt.subplot(2, 2, 4)
image_with_masks = image_bgr.copy()
for idx, row in enumerate(masks_filtradas_V2.itertuples()):  # Usamos itertuples para obter o índice numérico
    binary_mask = np.array(row.segmentation, dtype=np.uint8)
    contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        draw_contour_with_id(image_with_masks, cnt, idx, colors[idx % len(colors)])  # Cor diferente para cada máscara

plt.imshow(cv2.cvtColor(image_with_masks, cv2.COLOR_BGR2RGB))
plt.title('Original Image with Segmented Masks and IDs', fontsize=20)
plt.axis('off')

plt.tight_layout()
plt.show()

##############################
####### images processing
#############################

!pip install pillow
from PIL import Image
import seaborn as sns

##### Geração de DataFrame de listas a partir da segmentação
df = pd.DataFrame(masks_filtradas_V2)
df['predicted_iou'].mean()
df['stability_score'].mean()

altura, largura, _ = imagem_redimensionada.shape
largura_imagem_metros = 1.2
altura_imagem_metros = 1.2
largura_imagem_pixels = largura
altura_imagem_pixels = altura
resolucao_largura_metros_por_pixel = largura_imagem_metros / largura_imagem_pixels
resolucao_altura_metros_por_pixel = altura_imagem_metros / altura_imagem_pixels
resolucao_centimetros_por_metro = 100  # Fator de conversão de metros para centímetros

# Calculando a resolução em centímetros por pixel
resolucao_largura_centimetros_por_pixel = resolucao_largura_metros_por_pixel * resolucao_centimetros_por_metro
resolucao_altura_centimetros_por_pixel = resolucao_altura_metros_por_pixel * resolucao_centimetros_por_metro

# Calculando a área da folha em centímetros quadrados
df['area_cm_quadrados'] = df['area'] * resolucao_largura_centimetros_por_pixel * resolucao_altura_centimetros_por_pixel

import cv2
import numpy as np
import pandas as pd
from skimage import measure


def calcular_perimetros(df, resolucao_largura_centimetros_por_pixel):
    perimeters = []
    for mask_segmentation in df['segmentation']:
        binary_mask = np.where(mask_segmentation > 0, 255, 0).astype(np.uint8)  # Convert mask to binary (0 or 255)
        contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) > 0:
            max_perimeter = max(cv2.arcLength(contour, True) for contour in contours)
            perimeter = max_perimeter * resolucao_largura_centimetros_por_pixel
            perimeters.append(perimeter)
        else:
            print("No contours found for a mask")
            perimeters.append(np.nan)
    df['perimeter'] = perimeters
    return df

# Função para calcular as larguras máximas das máscaras de segmentação
def calcular_larguras_maximas(df, resolucao_largura_centimetros_por_pixel):
    larguras = []
    for _, row in df.iterrows():
        mask_segmentation = row['segmentation']
        binary_mask = np.where(mask_segmentation > 0, 255, 0).astype(np.uint8)
        contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            maior_contorno = max(contours, key=cv2.contourArea)
            x, y, largura, altura = cv2.boundingRect(maior_contorno)
            largura_cm = largura * resolucao_largura_centimetros_por_pixel
            larguras.append(largura_cm)
        else:
            larguras.append(np.nan)  # Adiciona NaN se nenhum contorno for encontrado
    df['largura_max'] = larguras
    return df

# Calculando os perímetros das máscaras de segmentação
df = calcular_perimetros(df, resolucao_largura_centimetros_por_pixel)

# Calculando as larguras máximas das máscaras de segmentação
df = calcular_larguras_maximas(df, resolucao_largura_centimetros_por_pixel)

# Calculando o comprimento máximo da folha em centímetros
comprimentos = []
for i, row in df.iterrows():
    mask_segmentation = row['segmentation']
    binary_mask = np.where(mask_segmentation > 0, 255, 0).astype(np.uint8)
    contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    maior_contorno = max(contours, key=cv2.contourArea)
    x, y, largura, altura = cv2.boundingRect(maior_contorno)
    altura_cm = altura * resolucao_altura_centimetros_por_pixel
    comprimentos.append(altura_cm)
df['comprimento_max'] = comprimentos

# Calculando a relação largura-comprimento da folha
df['relacao_largura_comprimento'] = df['comprimento_max'] / df['largura_max']
df['perimeter_area_ratio'] = df['perimeter'] / df['area_cm_quadrados']

# Exibindo o DataFrame atualizado
print(df)


import numpy as np
from scipy.spatial.distance import cdist

def functional_diversity_metrics(data):
    data_array = np.array(data)
    mean_value = np.mean(data_array)
    median_value = np.median(data_array)
    size_value = np.max(data_array) - np.min(data_array)
    std_deviation = np.std(data_array)
    coefficient_of_variation = 100*std_deviation / mean_value

    mean_value = round(mean_value, 1)
    median_value = round(median_value, 1)
    size_value = round(size_value, 1)
    coefficient_of_variation = round(coefficient_of_variation, 1)

    return mean_value, median_value, size_value, coefficient_of_variation

# calculando function FD
mean_value_area, median_value_area, size_value_area, coefficient_of_variation_area = functional_diversity_metrics(df['area_cm_quadrados'])
mean_value_perimeter, median_value_perimeter, size_value_perimeter, coefficient_of_variation_perimeter = functional_diversity_metrics(df['perimeter'])
mean_value_perimeter_area_ratio, median_value_perimeter_area_ratio, size_value_perimeter_area_ratio, coefficient_of_variation_perimeter_area_ratio = functional_diversity_metrics(df['perimeter_area_ratio'])
mean_value_LW, median_value_LW, size_value_LW, coefficient_of_variation_LW = functional_diversity_metrics(df['relacao_largura_comprimento'])


#################################
# Criação da figura e dos subplots

import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

fig, axs = plt.subplots(2, 3, figsize=(18, 12))

# Subplot 1: Histograma da área
sns.histplot(data=df, x='area_cm_quadrados', bins=range(0, int(df['area_cm_quadrados'].max()) + 10, 10), kde=True, color='#7e4a35', ax=axs[0, 0])
axs[0, 0].set_title('Leaf Litter Area', loc='left')
axs[0, 0].set_xlabel('cm²')
axs[0, 0].set_ylabel('Frequency')
axs[0, 0].grid(False)
axs[0, 0].spines[['top', 'right']].set_visible(False)
axs[0, 0].spines['bottom'].set_color('black')
axs[0, 0].spines['left'].set_color('black')

# Filter out NaN values from the 'perimeter' column
perimeter_data = df['perimeter'].dropna()

# Check if there are any valid values left after filtering
if not perimeter_data.empty:
    # Plot the histogram with valid data
    sns.histplot(data=df, x='perimeter', bins=range(0, int(perimeter_data.max()) + 10, 10), kde=True, color='#cab577', ax=axs[0, 1])
    axs[0, 1].set_title('Leaf Litter Perimeter', loc='left')
    axs[0, 1].set_xlabel('cm')
    axs[0, 1].set_ylabel('')
    axs[0, 1].grid(False)
    axs[0, 1].spines[['top', 'right']].set_visible(False)
    axs[0, 1].spines['bottom'].set_color('black')
    axs[0, 1].spines['left'].set_color('black')
else:
    # Handle the case where there are no valid values
    print("No valid data to plot the histogram for the 'perimeter' column.")

# Subplot 3: Histograma da relação perímetro-área
sns.histplot(data=df, x='perimeter_area_ratio', bins=range(0, int(df['perimeter_area_ratio'].max()) + 2, 1), kde=True, color='#8b6f47', ax=axs[1, 0])
axs[1, 0].set_title('Leaf Litter Perimeter-to-Area Ratios', loc='left')
axs[1, 0].set_xlabel('cm.cm⁻²')
axs[1, 0].set_ylabel('')
axs[1, 0].grid(False)
axs[1, 0].spines[['top', 'right']].set_visible(False)
axs[1, 0].spines['bottom'].set_color('black')
axs[1, 0].spines['left'].set_color('black')

# Subplot 4: Histograma da relação comprimento-largura
sns.histplot(data=df, x='relacao_largura_comprimento', bins=range(0, int(df['relacao_largura_comprimento'].max()) + 2, 1), kde=True, color='#7b5251', ax=axs[1, 1])
axs[1, 1].set_title('Leaf Litter Length-to-Width Ratios', loc='left')
axs[1, 1].set_xlabel('Ratio')
axs[1, 1].set_ylabel('')
axs[1, 1].grid(False)
axs[1, 1].spines[['top', 'right']].set_visible(False)
axs[1, 1].spines['bottom'].set_color('black')
axs[1, 1].spines['left'].set_color('black')

# Calculando métricas
litter_cover = (df['area_cm_quadrados'].sum() / 10000) * 100
numero_de_folhas = df.shape[0]
pred_iou = 100*(df['predicted_iou'].mean())
stab_score = 100*(df['stability_score'].mean())

# Texto com os resultados
text_str = f"Mean Predicted IoU: {pred_iou:.2f}%\n" \
           f"Mean Stability Score: {stab_score:.2f}%\n\n" \
           f"Litter Cover: {litter_cover:.2f}%\n" \
           f"Number of Leaf Litter Segmented: {numero_de_folhas}\n" \
           f"Area Metrics (cm²)\n" \
           f"Mean: {mean_value_area:.1f}\n" \
           f"Median: {median_value_area:.1f}\n" \
           f"Richness: {size_value_area:.1f}\n" \
           f"Coefficient of Variation: {coefficient_of_variation_area:.1f}%\n\n" \
           f"Perimeter Metrics (cm)\n" \
           f"Mean: {mean_value_perimeter:.1f}\n" \
           f"Median: {median_value_perimeter:.1f}\n" \
           f"Richness: {size_value_perimeter:.1f}\n" \
           f"Coefficient of Variation: {coefficient_of_variation_perimeter:.1f}%\n\n" \
           f"Perimeter-to-Area Ratio Metrics (cm².cm-¹)\n" \
           f"Mean: {mean_value_perimeter_area_ratio:.1f}\n" \
           f"Median: {median_value_perimeter_area_ratio:.1f}\n" \
           f"Richness: {size_value_perimeter_area_ratio:.1f}\n" \
           f"Coefficient of Variation: {coefficient_of_variation_perimeter_area_ratio:.1f}%\n\n" \
           f"Length-Width Ratio Metrics (cm².cm-¹)\n" \
           f"Mean: {mean_value_LW:.1f}\n" \
           f"Median: {median_value_LW:.1f}\n" \
           f"Richness: {size_value_LW:.1f}\n" \

# Exibir o texto com os resultados na coluna 3, linha 1
axs[0, 2].text(0.05, 0.5, text_str, verticalalignment='center', horizontalalignment='left', fontsize=10, color='black')
# Remover eixos da coluna 3, linha 1
axs[0, 2].axis('off')
axs[1, 2].axis('off')

plt.tight_layout()
plt.show()


# Create a dictionary with the metrics
metrics_dict = {
    "Litter Cover (%)": [litter_cover],
    "Number of Leaf Litter Segmented": [numero_de_folhas],
    "Mean Predicted IoU (%)": [pred_iou],
    "Mean Stability Score (%)": [stab_score],
    "Area Metrics Mean (cm²)": [mean_value_area],
    "Area Metrics Median (cm²)": [median_value_area],
    "Area Metrics Richness (cm²)": [size_value_area],
    "Area Metrics Coefficient of Variation (%)": [coefficient_of_variation_area],
    "Perimeter Metrics Mean (cm)": [mean_value_perimeter],
    "Perimeter Metrics Median (cm)": [median_value_perimeter],
    "Perimeter Metrics Richness (cm)": [size_value_perimeter],
    "Perimeter Metrics Coefficient of Variation (%)": [coefficient_of_variation_perimeter],
    "Perimeter-to-Area Ratio Metrics Mean (cm².cm⁻1)": [mean_value_perimeter_area_ratio],
    "Perimeter-to-Area Ratio Metrics Median (cm².cm⁻1)": [median_value_perimeter_area_ratio],
    "Perimeter-to-Area Ratio Metrics Richness (cm².cm⁻1)": [size_value_perimeter_area_ratio],
    "Perimeter-to-Area Ratio Metrics Coefficient of Variation (%)": [coefficient_of_variation_perimeter_area_ratio],
    "Lenght-Width Ratio Metrics Mean (cm.cm⁻1)": [mean_value_LW],
    "Lenght-Width Ratio Metrics Median (cm.cm⁻1)": [median_value_LW],
    "Lenght-Width Ratio Metrics Richness (cm.cm⁻1)": [size_value_LW],
    "Lenght-Width Ratio Metrics Coefficient of Variation (%)": [coefficient_of_variation_LW]

}

# Create a DataFrame from the dictionary
metrics_df = pd.DataFrame(metrics_dict)

nome_arquivo_sem_extensao = os.path.splitext(os.path.basename(caminho_imagem))[0]

# Nome do arquivo CSV com o sufixo "_general"
nome_arquivo_csv = nome_arquivo_sem_extensao + '_general.csv'

# Salvar DataFrame em um arquivo CSV
metrics_df.to_csv(nome_arquivo_csv, index=False)

############################
#### plot RGB indices
#######

import cv2
import numpy as np
import matplotlib.pyplot as plt

def calculate_indices(image_bgr):
    red_channel = image_bgr[:, :, 2]
    green_channel = image_bgr[:, :, 1]
    blue_channel = image_bgr[:, :, 0]


    ndvi = (green_channel - red_channel) / (green_channel + red_channel)
    gcc = green_channel / (image_bgr.sum(axis=2))
    excess_green = red_channel + blue_channel - 2 * green_channel
    Modified_Inverse_excess_green_1 = (blue_channel + 2 * red_channel) - 2 * green_channel
    Modified_Inverse_excess_green_2 = (2 * blue_channel + red_channel) - 2 * green_channel

    return ndvi, gcc, excess_green, Modified_Inverse_excess_green_1, Modified_Inverse_excess_green_2


# Calcule os índices
ndvi, gcc, excess_green, Modified_Inverse_excess_green_1, Modified_Inverse_excess_green_2 = calculate_indices(image_bgr)

# Crie mapas de cores
cmaps = ['RdYlBu_r', 'RdYlGn_r', 'viridis', 'RdYlBu_r']  # Escolha mapas de cores adequados

import cv2
import matplotlib.pyplot as plt
import numpy as np

fig, axs = plt.subplots(4, 2, figsize=(12, 18))

# Source Image
axs[0, 0].imshow(cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB))
axs[0, 0].set_title('Source Image')
axs[0, 0].axis('off')

# SAM Segmented Image
axs[0, 1].imshow(annotated_image, cmap=cmaps[0])
axs[0, 1].set_title('SAM Segmented Image')
axs[0, 1].axis('off')

# GCC
imA = axs[1, 0].imshow(gcc, cmap=cmaps[2])
axs[1, 0].set_title('GCC')
axs[1, 0].axis('off')
fig.colorbar(imA, ax=axs[1, 0], orientation='vertical')

# Excess Green
imB = axs[1, 1].imshow(excess_green, cmap=cmaps[3])
axs[1, 1].set_title('Excess Green')
axs[1, 1].axis('off')
fig.colorbar(imB, ax=axs[1, 1], orientation='vertical')

# Modified Inverse Excess Green 1
imC = axs[2, 0].imshow(Modified_Inverse_excess_green_1, cmap=cmaps[3])
axs[2, 0].set_title('Modified Inverse Excess Green 1')
axs[2, 0].axis('off')
fig.colorbar(imC, ax=axs[2, 0], orientation='vertical')

# Modified Inverse Excess Green 2
imD = axs[2, 1].imshow(Modified_Inverse_excess_green_2, cmap=cmaps[3])
axs[2, 1].set_title('Modified Inverse Excess Green 2')
axs[2, 1].axis('off')
fig.colorbar(imD, ax=axs[2, 1], orientation='vertical')

# Deixando o último subplot em branco
axs[3, 0].axis('off')
axs[3, 1].axis('off')

plt.tight_layout()
plt.show()

###################
##### image processing HIGH! Criação dos indices espectrais por ROI/folha segmentada

import cv2
import numpy as np
import pandas as pd

# Função para calcular índices
def calculate_indices(image_bgr):
    red_channel = image_bgr[:, :, 2]
    green_channel = image_bgr[:, :, 1]
    blue_channel = image_bgr[:, :, 0]

    ndvi = (green_channel - red_channel) / (green_channel + red_channel + blue_channel + 1e-8)
    gcc = green_channel / (image_bgr.sum(axis=2) + 1e-8)
    excess_green = red_channel + blue_channel - 2 * green_channel
    Modified_Inverse_excess_green_1 = (blue_channel + 2 * red_channel) - 2 * green_channel
    Modified_Inverse_excess_green_2 = (2 * blue_channel + red_channel) - 2 * green_channel

    return ndvi, gcc, excess_green, Modified_Inverse_excess_green_1, Modified_Inverse_excess_green_2

# Calcular índices
ndvi, gcc, excess_green, Modified_Inverse_excess_green_1, Modified_Inverse_excess_green_2 = calculate_indices(image_bgr)


# Inicializar DataFrame para armazenar média e variância de cada máscara
result_df = pd.DataFrame(columns=['Mask', 'NDVI_Mean', 'NDVI_Variance',
                                   'GCC_Mean', 'GCC_Variance', 'Excess_Green_Mean', 'Excess_Green_Variance',
                                   'MI_Excess_Green_1_Mean', 'MI_Excess_Green_1_Variance',
                                   'MI_Excess_Green_2_Mean', 'MI_Excess_Green_2_Variance'])

# Iterar sobre as linhas do DataFrame
for idx, row in df.iterrows():
    # Extrair 'segmentation' do DataFrame
    mask_segmentation = row['segmentation']
    binary_mask = np.where(mask_segmentation > 0, 255, 0).astype(np.uint8)  # Convertendo a máscara para binário (0 ou 255)

    # Redimensionar a máscara para coincidir com as dimensões dos índices
    resized_mask = cv2.resize(binary_mask, (ndvi.shape[1], ndvi.shape[0]))

    # Usar np.broadcast_to para garantir que a máscara tenha as mesmas dimensões que os índices
    mask = np.broadcast_to(resized_mask, ndvi.shape)

    # Aplicar a máscara em cada índice
    ndvi_masked = np.ma.masked_array(ndvi, ~mask)
    gcc_masked = np.ma.masked_array(gcc, ~mask)
    excess_green_masked = np.ma.masked_array(excess_green, ~mask)
    modified_excess_green_1_masked = np.ma.masked_array(Modified_Inverse_excess_green_1, ~mask)
    modified_excess_green_2_masked = np.ma.masked_array(Modified_Inverse_excess_green_2, ~mask)

    # Calcular média e variância para cada índice na máscara
    ndvi_mean = np.mean(ndvi_masked)
    ndvi_variance = np.var(ndvi_masked)
    gcc_mean = np.mean(gcc_masked)
    gcc_variance = np.var(gcc_masked)
    excess_green_mean = np.mean(excess_green_masked)
    excess_green_variance = np.var(excess_green_masked)
    modified_excess_green_1_mean = np.mean(modified_excess_green_1_masked)
    modified_excess_green_1_variance = np.var(modified_excess_green_1_masked)
    modified_excess_green_2_mean = np.mean(modified_excess_green_2_masked)
    modified_excess_green_2_variance = np.var(modified_excess_green_2_masked)

  # Inicializar DataFrame para armazenar média e variância de cada máscara
result_df = pd.DataFrame(columns=['Mask', 'NDVI_Mean', 'NDVI_Variance',
                                   'GCC_Mean', 'GCC_Variance', 'Excess_Green_Mean', 'Excess_Green_Variance',
                                   'MI_Excess_Green_1_Mean', 'MI_Excess_Green_1_Variance',
                                   'MI_Excess_Green_2_Mean', 'MI_Excess_Green_2_Variance'])

# Exibir o DataFrame resultante
print(result_df)

# Supondo que 'idx' seja a coluna que você deseja usar para fazer a junção
merged_df = pd.merge(result_df, df, left_on='Mask', right_index=True)

# Exibir o DataFrame resultante
print(merged_df)
colunas_a_excluir = ['Mask', 'segmentation']
merged_df2 = merged_df.drop(colunas_a_excluir, axis=1)

nome_arquivo_sem_extensao = os.path.splitext(os.path.basename(caminho_imagem))[0]
# Nome do arquivo CSV com o sufixo "_perMasks"
nome_arquivo_csv = nome_arquivo_sem_extensao + '__perMasks.csv'

# Salvar DataFrame em um arquivo CSV
merged_df2.to_csv(nome_arquivo_csv, index=False)