 import QtQuick 1.0



 Rectangle {

     SystemPalette { id: activePalette }

     id: container

     property string text: "Button"
     property int size: 18
     property alias enabled: mouseArea.enabled
     signal clicked

     width: buttonLabel.width + 20; height: buttonLabel.height + 5
     border { width: 1; color: Qt.darker(activePalette.button) }
     smooth: true
     radius: 8
     opacity: enabled ? 1 : .5

     // color the button with a gradient
     gradient: Gradient {
         GradientStop {
             position: 0.0
             color: {
                 if (enabled && mouseArea.pressed)
                     return "#666666";
                 else
                     return "#888888"
             }
         }
         GradientStop { position: 1.0; color: "#666666";  }
     }

     MouseArea {
         id: mouseArea
         anchors.fill: parent
         onClicked: container.clicked();
     }

     Text {
         id: buttonLabel
         anchors.centerIn: container
         font.pixelSize: size
         color: activePalette.buttonText
         text: container.text
     }
 }
