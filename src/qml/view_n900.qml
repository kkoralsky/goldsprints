import Qt 4.7
import QtQuick 1.1

Item {
    id: r

    width: 640; height: 480;
    property int current: 0
    //property int dist: 0
    property bool yes_youre_racing: false
    property bool race_prepared: false

    Component.onCompleted: { cmd.show_results("_",0,0) }

    function start() {
        console.log('starrt')
    }

    function abort() {
        red_bar.width=0
        blue_bar.width=0
        yes_youre_racing=false
        race_prepared=false

    }

    function finish() {
        abort();
    	console.log('finish');
    }

    function new_race(blue, red) {
        blue_input.text=blue
        red_input.text=red

        race_prepared=true
    }

    function update_race(player,pos,time,speed) {
        if(player===0) {
            blue_bar.width=blue_bar.parent.width*pos/dist

        }
        else if(player===1) {
            red_bar.width=red_bar.parent.width*pos/dist

        }
    }

    Column {

        spacing: 35 
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        anchors.topMargin: 50

        Rectangle {
            border.color: "blue"; border.width: 4;
            anchors.topMargin: 10
            anchors.horizontalCenter: parent.horizontalCenter
            height: 60; width: 500

            Keys.onPressed: {
                if(race_prepared)
                    btn_start.cliked()
                else
                    btn_new_race.clicked()
            }

            Rectangle {
                id: blue_bar
                x:0;y:0
                height:parent.height
                color: parent.border.color
            }

            TextInput {
                anchors.verticalCenter: parent.verticalCenter;
                anchors.margins: 4
                anchors.fill: parent
                validator:  RegExpValidator { regExp: /.{,15}/}
                font.pixelSize: 37
                font.bold: yes_youre_racing
                enabled: ! yes_youre_racing
                focus: true
                id: blue_input
                KeyNavigation.tab: red_input
                KeyNavigation.down: red_input
            }
        }

        Rectangle {
            border.color: "red"; border.width: 4; height: 60; width: 500
            anchors.horizontalCenter: parent.horizontalCenter

            Keys.onEnterPressed: {
                if(race_prepared)
                    btn_start.clicked();
                else
                    btn_new_race.clicked();
            }

            Rectangle {
                id: red_bar
                x:0;y:0
                height:parent.height

                color: parent.border.color
            }
            TextInput {
                font.pixelSize: 37;
                //font.bold: yes_youre_racing
                anchors { margins:4; verticalCenter: parent.verticalCenter; fill: parent }
                id: red_input
                font.bold: yes_youre_racing
                enabled: ! yes_youre_racing
                validator: RegExpValidator { regExp: /.{,15}/ }
                KeyNavigation.tab: blue_input
                KeyNavigation.up: blue_input
            }

        }

        Row {
            spacing:  30
            anchors.horizontalCenter: parent.horizontalCenter

            Btn {
                text: "New race";
                enabled: ! yes_youre_racing
                id: btn_new_race;
                size: 50
                onClicked: {
                    if(race_prepared) {
                        red_input.text=""
                        blue_input.text=""
                        race_prepared=false
                    } else if (red_input.text.length+blue_input.text.length>0) {
                        cmd.set_dist(distance_input.text)
                        var res=cmd.new_race(blue_input.text, red_input.text, "_", "_")

                        if(res.search(/.+(blue) and.+(red)/))
                            race_prepared=true
                        else
                            console.log(res)
                    }
                }
            }

            Btn { text: "Swap";
                enabled: (! yes_youre_racing) && race_prepared;
                id: btn_swap;
                size: 50
                onClicked: {
                    var tmp_n=red_input.text
                    red_input.text=blue_input.text
                    blue_input.text=tmp_n
                    cmd.swap()
                }
            }

            Btn { text: yes_youre_racing ? "Abort" : "Start"
                id: btn_start;
                enabled: race_prepared
                size: 50
                onClicked: {
                    if(yes_youre_racing) {
                        abort()
                        cmd.abort()
                    } else {
                        cmd.start()
                        yes_youre_racing=true
                    }
                }
            }


        }
        Row {
            spacing: 20; anchors.horizontalCenter: parent.horizontalCenter

            Btn { size: 35; text: "show sponsors"; onClicked: cmd.sponsors() }
            TextInput {
                width: 260; height: 40;
                id: distance_input;
                enabled: ! yes_youre_racing;
                font.pixelSize: 35;
                color: "white";
                horizontalAlignment: Text.AlignHCenter
                text: "400"
                anchors { margins:4; verticalCenter: parent.verticalCenter; }
                validator: IntValidator { bottom: 10; top: 1000000}
                cursorVisible: false

                Keys.onUpPressed: { distance_input.text=parseInt(distance_input.text)+100 }
                Keys.onDownPressed: { distance_input.text=parseInt(distance_input.text)-100 }
                Keys.onLeftPressed: { distance_input.text=parseInt(distance_input.text)-10 }
                Keys.onRightPressed: { distance_input.text=parseInt(distance_input.text)+10 }
            }
            Btn {
                property bool showing_res: false
                size: 35; text: showing_res ? "stop show" : "show results";
                onClicked: {
                    if(showing_res)
                        cmd.abort()
                    else
                        cmd.show_results("_", 0, 5)

                    showing_res = !showing_res
                }
            }
        }

        ListView {
            Component.onCompleted: { console.log(count) }
            width: r.width
            height: r.height
            clip: true
            focus: true
            x: 10
            model: results
            delegate: Row {
                Text {
                    font.letterSpacing: 4
                    height: 30;
                    anchors.margins: 10
                    width: 50
                    text: index+1
                    font.pixelSize: 40
                    color: "white"
                }
                Text { 
                    font.letterSpacing: 4
                    height: 30;
                    anchors.margins: 10
                    text: name
                    width: 250
                    color: "white"
                    font.pixelSize: 40
                }
                Text {
                    font.letterSpacing: 4
                    height: 30;
                    anchors.margins: 10
                    text: result
                    color: "yellow"
                    font.pixelSize: 40
                }
            }
        }
    }
}



