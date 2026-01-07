export class IronEye {
    constructor(videoElementId, overlayElementId) {
        this.videoElement = document.getElementById(videoElementId);
        this.overlayElement = document.getElementById(overlayElementId);
    }

    async init() {
        console.log("IronEye Initialized (Stub)");
        // simulate camera delay
        setTimeout(() => {
            if (this.overlayElement) this.overlayElement.innerText = "Camera Active (Sim)";
            // Dispatch success event automatically for demo
            const event = new CustomEvent('ironeye-success', { detail: { image: "base64_placeholder" } });
            document.dispatchEvent(event);
        }, 1500);
    }
}
