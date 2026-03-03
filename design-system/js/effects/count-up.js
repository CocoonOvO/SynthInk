/**
 * CountUp Effect - 数字滚动效果
 * 让数字从0滚动到目标值
 * 
 * 使用：CountUp.init('.selector', { duration: 2000, suffix: '+' })
 */

const CountUp = {
    init(selector, options = {}) {
        const elements = document.querySelectorAll(selector);
        const config = {
            duration: options.duration || 2000,
            suffix: options.suffix || '',
            prefix: options.prefix || '',
            separator: options.separator || ',',
            decimals: options.decimals || 0
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !entry.target.dataset.counted) {
                    entry.target.dataset.counted = 'true';
                    this.animate(entry.target, config);
                }
            });
        }, { threshold: 0.5 });

        elements.forEach(el => observer.observe(el));
    },

    animate(el, config) {
        const target = parseFloat(el.dataset.countTarget) || 0;
        const startTime = performance.now();
        const startValue = 0;

        const update = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / config.duration, 1);
            
            // 使用 easeOutExpo 缓动
            const easeProgress = 1 - Math.pow(2, -10 * progress);
            const current = startValue + (target - startValue) * easeProgress;
            
            el.textContent = config.prefix + this.formatNumber(current, config) + config.suffix;
            
            if (progress < 1) {
                requestAnimationFrame(update);
            }
        };

        requestAnimationFrame(update);
    },

    formatNumber(num, config) {
        const fixed = num.toFixed(config.decimals);
        const parts = fixed.split('.');
        parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, config.separator);
        return parts.join('.');
    }
};

// 自动初始化带 data-count-target 属性的元素
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-count-target]').forEach(el => {
        const duration = parseInt(el.dataset.countDuration) || 2000;
        const suffix = el.dataset.countSuffix || '';
        CountUp.init(el, { duration, suffix });
    });
});

window.CountUp = CountUp;
