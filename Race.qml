import QtQuick 1.0

Rectangle {
    width: 150
    height: 60
    z: -1
    property alias blue_player: blue_t.text
    property alias red_player: red_t.text
    property string org_blue: modelData[0]
    property string org_red: modelData[1]

    Item {
    Rectangle { color: "blue"
        height: 15; width: 100
        x: 0; y: 15; z: 0
        TextInput { id:blue_t; anchors.centerIn: parent }
        MouseArea { anchors.fill: parent; onClicked: { blue_t.focus=true } }
    }

//    Btn { text:  "R"; size: 10
//        anchors.left: parent.children[0].right
//        anchors.top: parent.children[0].top
//        onClicked: { if(blue_player) console.log(cmd.rename(org_blue, blue_player)) }
//    }
    }

    Item {
    Rectangle { color: "red"
        height: 15; width: 100
        x: 0; y: 30; z: 0
        TextInput { id: red_t; anchors.centerIn: parent }
        MouseArea { anchors.fill: parent; onClicked: { red_t.focus=true } }
    }

//    Btn { text:  "R"; size: 10
//        anchors.left: parent.children[0].right
//        anchors.top: parent.children[0].top
//        onClicked: { if(red_player) console.log(cmd.rename(org_red, red_player)) }
//    }
    }

    Btn { text: "start"; size: 10
        onClicked: {
            parent.color="grey"
            if(red_player==='')
                cmd.promote(sets[current], red_player)
            else if(blue_player==='')
                 cmd.promote(sets[current], blue_player)
            else {
                if(red_player!=org_red) {
                    cmd.rename(org_red, red_player)
                    org_red=red_player
                }
                if(blue_player!=org_blue) {
                    cmd.rename(org_blue, blue_player)
                    org_blue=blue_player
                }
                red_input.text=red_player
                blue_input.text=blue_player
                race_prepared=true
                cmd.finals_race(blue_player, red_player, sets[current])
            }
        }
    }

//    MouseArea {
//        anchors.fill: parent
//        property bool held: false
//        drag.axis: Drag.YAxis
//        drag.minimumY: 0
//        drag.maximumY: 400
//        onPressed: {
//            drag.target=parent.children[Math.round(mouseY/parent.height)]
//            currentDrag=drag.target
//            drag.target.z=5000
//            drag.target.opacity=.5
//            held=true
//        }

//        onReleased: {
//            if(held) {
//                held=false
//                drag.target.z=0
//                drag.target.opacity=1
//                console.log(mouseY)
//            }
//        }
//    }
}
