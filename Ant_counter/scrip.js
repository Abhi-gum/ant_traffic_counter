const API_URL = "https://ant-traffic-counter-2.onrender.com";


async function uploadVideo() {

    const input =
        document.getElementById("videoInput");

    const status =
        document.getElementById("status");

    const resultVideo =
        document.getElementById("resultVideo");

    const count =
        document.getElementById("count");


    // --------------------------------------------------------
    // CHECK FILE
    // --------------------------------------------------------

    if (!input.files.length) {

        status.innerText =
            "Please select a video first.";

        return;
    }


    const file = input.files[0];


    // --------------------------------------------------------
    // FORM DATA
    // --------------------------------------------------------

    const formData =
        new FormData();

    formData.append(
        "file",
        file
    );


    status.innerText =
        "Uploading video... Please wait.";

    count.innerText = "";

    resultVideo.removeAttribute(
        "src"
    );

    resultVideo.load();


    try {

        // ----------------------------------------------------
        // SEND TO BACKEND
        // ----------------------------------------------------

        const response =
            await fetch(
                `${API_URL}/upload-video`,
                {
                    method: "POST",
                    body: formData
                }
            );


        if (!response.ok) {

            throw new Error(
                "Server error"
            );
        }


        const data =
            await response.json();


        // ----------------------------------------------------
        // CHECK RESULT
        // ----------------------------------------------------

        if (!data.success) {

            status.innerText =
                "Detection failed.";

            return;
        }


        // ----------------------------------------------------
        // SHOW COUNT
        // ----------------------------------------------------

        count.innerText =
            `🐜 Total Ants: ${data.count}`;


        // ----------------------------------------------------
        // SHOW RESULT VIDEO
        // ----------------------------------------------------

        resultVideo.src =
            `${API_URL}${data.video_url}?t=${Date.now()}`;

        resultVideo.load();


        status.innerText =
            "Detection completed successfully.";


    } catch (error) {

        console.error(error);

        status.innerText =
            "Error: Could not process video.";
    }
}


function startCounting() {

    document
        .getElementById("videoInput")
        .click();
}


function scrollToHow() {

    document
        .getElementById("how-it-works")
        .scrollIntoView({
            behavior: "smooth"
        });
}