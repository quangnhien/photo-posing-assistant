import cv2
import numpy as np

# Create a blank image
# image = np.zeros((500, 500, 3), dtype=np.uint8)

# # Draw an arc
# center = (250, 250)  # Center of the ellipse
# axes = (150, 200)    # Major and minor axes
# angle = 30            # Angle of the ellipse rotation
# start_angle = 30      # Starting angle of the arc
# end_angle = 150      # Ending angle of the arc
# color = (255, 0, 0)  # Line color (Blue in BGR)
# thickness = 2        # Line thickness

# cv2.ellipse(image, center, axes, angle, start_angle, end_angle, color, thickness)

# # Display the image
# cv2.imshow("Arc", image)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

import cv2
import numpy as np

# Create a blank image
image = np.zeros((500, 500, 3), dtype=np.uint8)

# Define line parameters
start_point = (100, 250)  # Starting point of the line
end_point = (300, 500)    # Ending point of the line
color = (0, 255, 0)       # Line color (Green in BGR)
thickness = 2             # Thickness of the line
tip_length = 0.2          # Length of the arrow tip relative to the line length

# Draw the arrowed line
cv2.arrowedLine(image, start_point, end_point, color, thickness, tipLength=tip_length)

# Display the image
cv2.imshow("Arrowed Line", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.arr

