import QtQuick 1.0

Rectangle {
    id: container

    property alias val: slider_val.text

    height: 16
    width: 100

    radius: 8
    opacity: 0.7
    smooth: true
    gradient: Gradient {
        GradientStop { position: 0.0; color: "gray" }
        GradientStop { position: 1.0; color: "white" }
    }

    Rectangle {
        id: slider
        width: 30; height: 14
        x: container.width/2-slider.width/2
        //anchors.horizontalCenter: parent.horizontalCenter

        radius: 6
        smooth: true
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#424242" }
            GradientStop { position: 1.0; color: "black" }
        }

        Text { id:slider_val; anchors.centerIn: parent; text: "8" }

        MouseArea {
            //hoverEnabled: true
            anchors.fill: parent
            //anchors.margins: -16 // Increase mouse area a lot outside the slider
            drag.target: parent; drag.axis: Drag.XAxis
            drag.minimumX: 2; drag.maximumX: container.width - 32
            onPositionChanged: {
                if(drag.active) {
                    var slide_pos=Math.round(3*slider.x/container.width)
                    if(slide_pos<=0) slider_val.text=4
                    else if(slide_pos==1) slider_val.text=8
                    else slider_val.text=16
                }
            }


//            onPressed: { drag.target=parent }
            onReleased: {
                var slide_pos=Math.round(3*slider.x/container.width)
                //console.log(slide_pos)
                drag.target.x=slide_pos*container.width/3
            }
        }
    }
}
