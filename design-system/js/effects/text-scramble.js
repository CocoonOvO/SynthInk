/**
 * TextScramble Effect - 文字扰乱/解码效果
 * 文字像被解密一样逐渐显现
 * 
 * 使用：TextScramble.init('.selector', { chars: '!<>-_\\/[]{}—=+*^?#________', speed: 50 })
 */

const TextScramble = {
    config: {
        chars: '!<>-_\\/[]{}—=+*^?#________',
        speed: 50,
        delay: 0
    },

    init(selector, options = {}) {
        const elements = document.querySelectorAll(selector);
        this.config = { ...this.config, ...options };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !entry.target.dataset.scrambled) {
                    entry.target.dataset.scrambled = 'true';
                    setTimeout(() => {
                        this.scramble(entry.target);
                    }, this.config.delay);
                }
            });
        }, { threshold: 0.5 });

        elements.forEach(el => observer.observe(el));
    },

    scramble(el) {
        const originalText = el.dataset.scrambleText || el.textContent;
        el.dataset.scrambleText = originalText;
        
        const length = originalText.length;
        let iteration = 0;
        
        const interval = setInterval(() => {
            el.textContent = originalText
                .split('')
                .map((char, index) => {
                    if (char === ' ') return ' ';
                    if (index < iteration) {
                        return originalText[index];
                    }
                    return this.config.chars[Math.floor(Math.random() * this.config.chars.length)];
                })
                .join('');

            if (iteration >= length) {
                clearInterval(interval);
                el.textContent = originalText;
            }

            iteration += 1/3;
        }, this.config.speed);
    }
};

// 自动初始化带 data-scramble 属性的元素
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-scramble]').forEach(el => {
        const speed = parseInt(el.dataset.scrambleSpeed) || 50;
        const delay = parseInt(el.dataset.scrambleDelay) || 0;
        TextScramble.init(el, { speed, delay });
    });
});

window.TextScramble = TextScramble;
