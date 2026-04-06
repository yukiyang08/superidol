<template>
  <div class="plate-loader" :class="`size-${size}`" role="status" aria-live="polite">
    <div class="loader-stage" aria-hidden="true">
      <div class="plate-spirit">
        <span class="plate-ring"></span>
        <span class="plate-ring-inner"></span>
        <span class="bowl-shell"></span>
        <span class="leaf leaf-left"></span>
        <span class="leaf leaf-right"></span>
        <span class="fork-handle"></span>
        <span class="spark spark-1"></span>
        <span class="spark spark-2"></span>
        <span class="star"></span>
      </div>
    </div>

    <p class="loader-message">{{ message }}</p>
    <p v-if="submessage" class="loader-submessage">{{ submessage }}</p>
  </div>
</template>

<script setup>
defineProps({
  message: {
    type: String,
    default: '餐盤小精靈備餐中...'
  },
  submessage: {
    type: String,
    default: ''
  },
  size: {
    type: String,
    default: 'md'
  }
})
</script>

<style scoped>
.plate-loader {
  --loader-size: 136px;
  --orange: #ff9a3d;
  --orange-soft: #ffd7a6;
  --green: #69c27d;
  --cream: #fff7eb;
  display: grid;
  justify-items: center;
  gap: 8px;
  text-align: center;
}

.plate-loader.size-sm {
  --loader-size: 102px;
}

.plate-loader.size-lg {
  --loader-size: 166px;
}

.loader-stage {
  width: var(--loader-size);
  height: var(--loader-size);
  position: relative;
  display: grid;
  place-items: center;
}

.plate-spirit {
  position: relative;
  width: 90%;
  height: 90%;
  animation: bob 2.3s ease-in-out infinite;
}

.plate-ring,
.plate-ring-inner {
  position: absolute;
  border-radius: 50%;
  border: 5px solid rgba(255, 168, 70, 0.92);
}

.plate-ring {
  inset: 16% 10% 12% 14%;
}

.plate-ring-inner {
  inset: 24% 18% 20% 22%;
  border-width: 3px;
  border-color: rgba(255, 215, 166, 0.8);
}

.bowl-shell {
  position: absolute;
  left: 40%;
  top: 48%;
  width: 32%;
  height: 16%;
  border: 3px solid var(--orange);
  border-top: 0;
  border-radius: 0 0 40px 40px;
  background: linear-gradient(180deg, var(--cream) 0%, #ffeecf 100%);
}

.bowl-shell::before {
  content: '';
  position: absolute;
  left: -6%;
  right: -6%;
  top: -16%;
  height: 3px;
  background: var(--orange);
  border-radius: 999px;
}

.leaf {
  position: absolute;
  width: 12%;
  height: 14%;
  background: linear-gradient(180deg, #8ee5a6 0%, var(--green) 100%);
  border-radius: 100% 0 100% 0;
  top: 36%;
  animation: leafWiggle 2.4s ease-in-out infinite;
}

.leaf::after {
  content: '';
  position: absolute;
  left: 48%;
  top: 14%;
  bottom: 12%;
  width: 1px;
  background: rgba(255, 255, 255, 0.65);
  transform: rotate(18deg);
}

.leaf-left {
  left: 49%;
  transform: rotate(-18deg);
}

.leaf-right {
  left: 58%;
  top: 38%;
  transform: rotate(18deg);
  animation-delay: 0.4s;
}

.fork-handle {
  position: absolute;
  right: 12%;
  top: 56%;
  width: 4%;
  height: 20%;
  border-radius: 999px;
  background: linear-gradient(180deg, #ffd8aa 0%, #ffb96d 100%);
  transform: rotate(30deg);
  transform-origin: center top;
  box-shadow: 0 0 0 1px rgba(255, 173, 84, 0.3);
}

.fork-handle::before,
.fork-handle::after {
  content: '';
  position: absolute;
  top: -18%;
  width: 38%;
  height: 20%;
  border-radius: 999px;
  background: #ffb76c;
}

.fork-handle::before {
  left: 20%;
}

.fork-handle::after {
  left: 44%;
}

.spark {
  position: absolute;
  border-radius: 50%;
  width: 8px;
  height: 8px;
  background: radial-gradient(circle at 35% 35%, #fffefc 0%, #ffe1b6 45%, #ffb456 100%);
  box-shadow: 0 0 12px rgba(255, 173, 84, 0.3);
  animation: sparkle 2.2s ease-in-out infinite;
}

.spark-1 {
  top: 18%;
  right: 14%;
}

.spark-2 {
  top: 24%;
  left: 16%;
  animation-delay: 0.9s;
}

.star {
  position: absolute;
  top: 8%;
  left: 52%;
  width: 14px;
  height: 14px;
  background: linear-gradient(180deg, #fff4d4 0%, #ffcb66 100%);
  clip-path: polygon(50% 0%, 61% 35%, 98% 35%, 68% 57%, 79% 92%, 50% 72%, 21% 92%, 32% 57%, 2% 35%, 39% 35%);
  animation: twinkle 2s ease-in-out infinite;
  filter: drop-shadow(0 2px 8px rgba(255, 192, 77, 0.24));
}

.loader-message {
  margin: 0;
  color: #83592f;
  font-size: 0.98rem;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.loader-submessage {
  margin: -4px 0 0;
  color: #9a7c56;
  font-size: 0.88rem;
  line-height: 1.5;
  max-width: 28ch;
}

@keyframes bob {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-5px);
  }
}

@keyframes leafWiggle {
  0%,
  100% {
    transform: rotate(-18deg);
  }
  50% {
    transform: rotate(-10deg);
  }
}

@keyframes sparkle {
  0%,
  100% {
    transform: translateY(0) scale(0.9);
    opacity: 0.45;
  }
  50% {
    transform: translateY(-5px) scale(1.15);
    opacity: 1;
  }
}

@keyframes twinkle {
  0%,
  100% {
    transform: scale(0.9) rotate(0deg);
    opacity: 0.7;
  }
  50% {
    transform: scale(1.12) rotate(8deg);
    opacity: 1;
  }
}

@media (max-width: 640px) {
  .plate-loader {
    --loader-size: 118px;
  }

  .plate-loader.size-sm {
    --loader-size: 92px;
  }

  .loader-message {
    font-size: 0.94rem;
  }

  .loader-submessage {
    font-size: 0.82rem;
  }
}
</style>