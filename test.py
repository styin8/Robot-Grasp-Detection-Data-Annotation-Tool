import numpy as np
import matplotlib.pyplot as plt



def read_and_visualize_dat(file_path):
    try:
        # Read data
        data = np.fromfile(file_path, dtype=np.float32)
        data = data.reshape((480, 640, 3))

        # Reshape data to (480, 640, 3)
        print(f"Data shape: {data.shape}")

        # Create a 1x3 subplot
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        # Display grasp quality heatmap
        quality_map, q_cmap, q_ticks, q_labels, q_title = apply_colormap(data[:, :, 0], 'quality')
        im0 = axes[0].imshow(quality_map)
        axes[0].set_title('Grasp Quality Heatmap')
        axes[0].axis('off')
        cbar0 = plt.colorbar(plt.cm.ScalarMappable(cmap=q_cmap), ax=axes[0])
        cbar0.set_ticks(q_ticks)
        cbar0.set_ticklabels(q_labels)
        cbar0.set_label(q_title)

        # Display grasp angle heatmap
        angle_data = data[:, :, 1]
        # Ensure angle data is within -90 to 90 degrees range
        angle_data = np.clip(angle_data, -90, 90)
        im1 = axes[1].imshow(angle_data, cmap='RdYlBu', vmin=-90, vmax=90)
        axes[1].set_title('Grasp Angle Heatmap')
        axes[1].axis('off')
        cbar1 = plt.colorbar(im1, ax=axes[1])
        # Set evenly distributed angle ticks
        cbar1.set_ticks([-90, -45, 0, 45, 90])
        cbar1.set_ticklabels(['-90°', '-45°', '0°', '45°', '90°'])
        cbar1.set_label('Angle (degrees)')

        # Display grasp width heatmap
        width_data = data[:, :, 2]
        # Process width data: take absolute value and limit range to 0-150mm
        width_data = np.abs(width_data)  # Take absolute value
        width_data = np.clip(width_data, 0, 150)  # Limit range
        im2 = axes[2].imshow(width_data, cmap='YlGnBu', vmin=0, vmax=150)
        axes[2].set_title('Grasp Width Heatmap')
        axes[2].axis('off')
        cbar2 = plt.colorbar(im2, ax=axes[2])
        # Set fixed tick range
        cbar2.set_ticks([0, 37.5, 75, 112.5, 150])
        cbar2.set_ticklabels(['0', '37.5', '75', '112.5', '150'])
        cbar2.set_label('Grasp Width (units)')

        plt.tight_layout()
        plt.show()
        return data

    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return None


def apply_colormap(data, type):
    """Apply heatmap color mapping"""
    if type == 'quality':
        # quality_map is already in 0-1 range, use directly
        normalized_data = np.clip(data, 0, 1)
        # Use YlOrRd colormap (from light yellow to deep red)
        cmap = plt.cm.YlOrRd
        colored = (cmap(normalized_data)[:, :, :3] * 255).astype(np.uint8)
        return colored, 'YlOrRd', [0, 0.5, 1], ['0', '0.5', '1'], 'Grasp Quality'
        
    elif type == 'angle':
        # Convert angle to radians
        angle_rad = np.deg2rad(data)
        # Calculate sin and cos
        sin_data = (np.sin(angle_rad) + 1) / 2  # Normalize to 0-1
        cos_data = (np.cos(angle_rad) + 1) / 2  # Normalize to 0-1
        
        # Use matplotlib colormap to generate colors
        sin_cmap = plt.cm.RdBu_r  # Use reversed red-blue map
        cos_cmap = plt.cm.GnBu_r  # Use reversed green-blue map
        sin_colors = (sin_cmap(sin_data)[:, :, :3] * 255).astype(np.uint8)
        cos_colors = (cos_cmap(cos_data)[:, :, :3] * 255).astype(np.uint8)
        
        return (sin_colors, cos_colors), ('RdBu_r', 'GnBu_r'), ([0, 0.5, 1], [0, 0.5, 1]), (['-1', '0', '1'], ['-1', '0', '1']), ('Sin Value', 'Cos Value')
        
    elif type == 'width':
        # width_map range is 0 to 150, use fixed range normalization
        normalized_data = np.clip(data / 150, 0, 1)  # Use fixed maximum value of 150
        # Use YlGnBu colormap (from light yellow to blue-green)
        cmap = plt.cm.YlGnBu
        colored = (cmap(normalized_data)[:, :, :3] * 255).astype(np.uint8)
        # Set fixed tick values
        ticks = [0, 0.25, 0.5, 0.75, 1]
        tick_labels = ['0', '37.5', '75', '112.5', '150']  # Fixed width ticks
        return colored, 'YlGnBu', ticks, tick_labels, 'Grasp Width (units)'

    else:
        # Default case, use viridis colormap
        normalized_data = np.clip(data, 0, 1)
        cmap = plt.cm.viridis
        colored = (cmap(normalized_data)[:, :, :3] * 255).astype(np.uint8)
        return colored, 'viridis', [0, 0.5, 1], ['0', '0.5', '1'], 'Value'


# Usage example
if __name__ == "__main__":
    file_path = "/path/to/your/file.mat"
    data = read_and_visualize_dat(file_path)
    
    if data is not None:
        # Get angle data and display sin/cos decomposition
        angle_data = data[:, :, 1]
        
        # Create new figure to display sin and cos components
        fig, (ax_sin, ax_cos) = plt.subplots(1, 2, figsize=(12, 6))
        
        # Calculate and display sin/cos components
        (sin_map, cos_map), (s_cmap, c_cmap), (s_ticks, c_ticks), (s_labels, c_labels), (s_title, c_title) = apply_colormap(angle_data, 'angle')
        
        # Display sin component
        im_sin = ax_sin.imshow(sin_map)
        ax_sin.set_title('Angle Sin Component', fontsize=12)
        ax_sin.axis('off')
        cbar_sin = plt.colorbar(plt.cm.ScalarMappable(cmap=s_cmap), ax=ax_sin)
        cbar_sin.set_ticks(s_ticks)
        cbar_sin.set_ticklabels(s_labels)
        cbar_sin.set_label(s_title, fontsize=10)
        
        # Display cos component
        im_cos = ax_cos.imshow(cos_map)
        ax_cos.set_title('Angle Cos Component', fontsize=12)
        ax_cos.axis('off')
        cbar_cos = plt.colorbar(plt.cm.ScalarMappable(cmap=c_cmap), ax=ax_cos)
        cbar_cos.set_ticks(c_ticks)
        cbar_cos.set_ticklabels(c_labels)
        cbar_cos.set_label(c_title, fontsize=10)
        
        plt.tight_layout()
        plt.show()
