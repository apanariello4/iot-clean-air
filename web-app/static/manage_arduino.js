const button = document.getElementById('post-btn');
const remove_button = document.getElementById('remove-arduino')

var status = document.querySelector('#stat').value
var command = (status == 'False')

var this_path = window.location.href
var base_url = window.location.origin

var arduino_uuid = this_path.substring(this_path.lastIndexOf('/') + 1);

var qrc = new QRCode(document.getElementById("qrcode"), {
    width: 128,
    height: 128
});

qrc.makeCode(arduino_uuid);

button.addEventListener('click', async _ => {
    try {
        const response = await fetch(this_path, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                "status": command
            })
        });
        console.log('status val:', status, command);
        console.log('Completed!', response);
        if (response.ok) {
            alert("Request sent succesfully");
        } else {
            alert("Request failed")
        }
    } catch (err) {
        console.error(`Error: ${err}`);
    }


});
remove_button.addEventListener('click', async _ => {
    try {
        const response = await fetch(base_url + '/api/v1/sensor/remove?arduino_uuid=' + arduino_uuid);
        if (response.ok) {
            alert("Arduino removed");
            window.location.replace(base_url + '/list');
        } else {
            alert("Request failed")
        }
    } catch (err) {
        console.error(`Error: ${err}`);
    }
});

var clientId = "browser-" + Math.floor((Math.random() * 1000) + 1);

var client = new Paho.Client('151.81.28.142', Number('4000'), clientId);

// set callback handlers
client.onConnectionLost = onConnectionLost;
client.onMessageArrived = onMessageArrived;
// connect the client
client.connect({ onSuccess: onConnect, reconnect: true, keepAliveInterval: 10 });


// called when the client connects
function onConnect() {
    // Once a connection has been made, make a subscription and send a message.
    console.log("Connected");
    client.subscribe(arduino_uuid + '/window');
    console.log("Subscribed to: " + arduino_uuid + '/window')

}

// called when the client loses its connection
function onConnectionLost(responseObject) {
    if (responseObject.errorCode !== 0) {
        console.log("onConnectionLost:" + responseObject.errorMessage);
    }
}

// called when a message arrives
function onMessageArrived(message) {
    console.log("Message arrived:" + message.payloadString + " Refreshing");
    client.disconnect();
    window.location.reload();
}
