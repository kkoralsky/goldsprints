import QtQuick 1.0

Item {
    property string id
    property variant races
    width: 150
    height: parent.height

    Column {
        z: -1
        spacing: 10
        Repeater {
            z: -1
            model: races
            delegate: Race { blue_player: modelData[0]; red_player: modelData[1] }
        }
    }

//    MouseArea {
//        anchors.fill: parent
//        id: globalDragArea
//        property int currentDrag
//        drag.axis: Drag.YAxis
//        drag.filterChildren: true
//        onPressed: {
//            var race_n=Math.floor(mouseY/70)
//            var pl_n=Math.round(mouseY%70/70)
//            var dragged_el=parent.children[0].children[race_n].children[pl_n]
//            console.log(race_n, pl_n)
//            dragged_el.parent=parent
//            //dragged_el.x=mouseX
//            dragged_el.y=mouseY

//            drag.target=dragged_el

//            //drag.target.parent=parent
//            //drag.target.y=mouseY-20//Math.floor(mouseY/70)*70
//            drag.target.z=3

//            drag.target.opacity=.5
//        }

//        onReleased: {
//            var race_n=Math.floor(mouseY/70)
//            var pl_n=Math.round(mouseY%70/70)
//            drag.target.opacity=1
//            drag.target.z=0
//            drag.target.parent=parent.children[0].children[race_n]
//            parent.children[0].children[race_n].children[pl_n]=drag.target

//        }


//    }
}
