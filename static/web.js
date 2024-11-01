function test() {
	alert('Hello World');
}

let music = new Audio();

let showing = false;

music.addEventListener('timeupdate', () => {
  const percent = music.currentTime / music.duration * 100;
  seeker.value = percent;
  updateTimeTexts();
});


function showPlayer() {
	if (showing) {
		return;
	}

	showing = true;

	document.querySelector('#player').style.display = 'flex';

	const seeker = document.querySelector('#seeker');
	const volume = document.querySelector("#volume-control");

	seeker.addEventListener('input', (e) => {
		music.currentTime = e.target.value / 100 * music.duration;
	});

	volume.addEventListener("input", function(e) {
		music.volume = e.currentTarget.value / 100;
	})

	const playButton = document.querySelector('#play-button');
	playButton.addEventListener('click', () => {
		if (music.paused) {
			playMusic("");
		} else {
			pauseMusic();
		}
	});

	updateTimeTexts();
}

function updateTimeTexts() {
	const timeCurrent = document.querySelector('#time-current');
	const timeFull = document.querySelector('#time-full');

	let time = music.currentTime;
	if (isNaN(time)) {
		time = '-:--';
	} else {
		time = formatTime(time);
	}
	let duration = music.duration;
	if (isNaN(duration)) {
		duration = '-:--';
	} else {
		duration = formatTime(duration);
	}

	timeCurrent.innerText = time;
	timeFull.innerText = duration;
}

function formatTime(time) {
	const minutes = Math.floor(time / 60);
	const seconds = Math.floor(time % 60);
	return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
}

function playMusic(url) {
	showPlayer();

	if (url != "") {
		music.src = url;
	}

	music.play();


	const playIcon = document.querySelector('#play-icon');
	playIcon.className = 'bi bi-pause-fill';
}

function pauseMusic() {
	music.pause();

	const playIcon = document.querySelector('#play-icon');
	playIcon.className = 'bi bi-play-fill';
}