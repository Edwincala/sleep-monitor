const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const earSpan = document.getElementById('ear');
const closedSpan = document.getElementById('closed');
const alertBox = document.getElementById('alert');

let wasAsleep = false;

navigator.mediaDevices.getUserMedia({video: true})
.then((stream) => {
    video.srcObject = stream;
})
.catch((err) => {
    console.error(err);
});

async function sendFrame() {
    const ctx = canvas.getContext("2d");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(async (blob) => {
        const formData = new FormData();
        formData.append("file", blob, "frame.jpg");

        try {
            const res = await fetch("/predict-frame", {
                method: "POST",
                body: formData
            });

            if(!res.ok) {
                console.warn("Error en la respuesta del backend:", res.status);
                return;
            }

            const data = await res.json();
            
            if(data.ear !== null && data.ear !== undefined){
                earSpan.textContent = data.ear.toFixed(3);
            } else {
                earSpan.textContent = "No detectado";
            }

            closedSpan.textContent = data.sleep_alert ? "Sí" : "No";

            if (data.sleep_alert) {
                alertBox.style.display = 'block';

                if(!wasAsleep) {
                    document.getElementById('alertSound').play();
                    wasAsleep = true;
                }
            } else {
                alertBox.style.display = 'none';
                wasAsleep = false;
            }

        } catch (error) {
            console.error("Error al enviar frame: ", error);
        }
    }, "image/jpeg");
}

setInterval(() => {
    if(video.readyState === 4) {
        sendFrame();
    }
}, 500);