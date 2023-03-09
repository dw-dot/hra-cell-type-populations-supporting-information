#Load the required libraries
library(googlesheets4)
library("tidyverse")

# load data
raw = read_sheet('https://docs.google.com/spreadsheets/d/1cwxztPg9sLq0ASjJ5bntivUk6dSKHsVyR1bE6bXvMkY/edit#gid=0', skip=1)

# rename columns
cols_renamed = raw %>% 
  select(source,organ, HuBMAP_tissue_block_id, rui_location_id, number_of_cells_total, `tissue_block_volume (if registered) [millimeters^3]`, `cta... (Azimuth, popV, Ctypist)`, omap, unique_CT_for_tissue_block) %>% 
  rename(
    tissue_block_volume= `tissue_block_volume (if registered) [millimeters^3]`,
    cta = `cta... (Azimuth, popV, Ctypist)`
  )
cols_renamed

# number of tissue blocks with RUI but without CT info; 643 on March 9, 2023
cols_renamed %>% 
  select(-cta, -omap) %>% 
  filter(!is.na(tissue_block_volume), is.na(number_of_cells_total)) %>% 
  group_by(HuBMAP_tissue_block_id)

# format data for scatter graph
scatter = cols_renamed%>% 
  filter(!is.na(tissue_block_volume),!is.na(number_of_cells_total)) %>% 
  group_by(
    HuBMAP_tissue_block_id, 
    tissue_block_volume, 
    unique_CT_for_tissue_block,
    organ
    ) %>% 
  summarise(total_per_tissue_block = sum(number_of_cells_total)) %>% 
  filter(!total_per_tissue_block>200000)

scatter

# visualize as scatter graph
ggplot(data = scatter, aes(x = tissue_block_volume, y = total_per_tissue_block, color=organ))+
  geom_point(
    size=scatter$unique_CT_for_tissue_block/10, alpha=.5
    )+
  geom_text(aes(x = tissue_block_volume+1, y = total_per_tissue_block, label=unique_CT_for_tissue_block), nudge_x=.5, size=5) +
  guides(color = guide_legend(title = "Organ"))+
   scale_color_brewer(type="qual",palette=2,direction=-1)+
  ggtitle("Total number of cells per tissue block over volume")+
 labs(y = "Total number of cells per tissue block", x = "Volume of tissue block")+
scatter_theme


scatter_theme <- theme(
  plot.title = element_text(family = "Helvetica", face = "bold", size = (20)),
  legend.title = element_text(colour = "black", face = "bold.italic", family = "Helvetica"),
  legend.text = element_text(face = "italic", colour = "black", family = "Helvetica"),
  axis.title = element_text(family = "Helvetica", size = (20), colour = "black"),
  axis.text = element_text(family = "Courier", colour = "black", size = (20)),
  legend.key.size = unit(1,"line"), legend.position = "bottom"
)
