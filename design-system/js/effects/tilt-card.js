/**
 * TiltCard Effect - 3D卡片倾斜效果
 * 鼠标悬停时卡片产生3D倾斜
 * 
 * 使用：TiltCard.init('.card-selector', { maxTilt: 15, perspective: 1000 })
 */

const TiltCard = {
    config: {
        maxTilt: 15,
        perspective: 1000,
        scale: 1.02,
        speed: 400,
        glare: true,
        maxGlare: 0.3
    },

    init(selector, options = {}) {
        const elements = document.querySelectorAll(selector);
        this.config = { ...this.config, ...options };

        elements.forEach(el => {
            this.bindEvents(el);
        });
    },

    bindEvents(el) {
        // 触摸设备跳过
        if (window.matchMedia('(pointer: coarse)').matches) return;

        el.style.transformStyle = 'preserve-3d';
        el.style.transition = `transform ${this.config.speed}ms ease`;

        if (this.config.glare) {
            this.createGlare(el);
        }

        el.addEventListener('mousemove', (e) => this.handleMouseMove(e, el));
        el.addEventListener('mouseleave', () => this.handleMouseLeave(el));
        el.addEventListener('mouseenter', () => this.handleMouseEnter(el));
    },

    createGlare(el) {
        const glare = document.createElement('div');
        glare.className = 'tilt-glare';
        glare.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            border-radius: inherit;
            background: linear-gradient(135deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0) 100%);
            pointer-events: none;
            z-index: 10;
            opacity: 0;
            transition: opacity ${this.config.speed}ms ease;
        `;
        el.appendChild(glare);
        el.dataset.glare = 'true';
    },

    handleMouseMove(e, el) {
        const rect = el.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        
        const rotateX = ((y - centerY) / centerY) * -this.config.maxTilt;
        const rotateY = ((x - centerX) / centerX) * this.config.maxTilt;

        el.style.transform = `
            perspective(${this.config.perspective}px)
            rotateX(${rotateX}deg)
            rotateY(${rotateY}deg)
            scale3d(${this.config.scale}, ${this.config.scale}, ${this.config.scale})
        `;

        // 更新反光
        if (el.dataset.glare === 'true') {
            const glare = el.querySelector('.tilt-glare');
            if (glare) {
                const glareX = (x / rect.width) * 100;
                const glareY = (y / rect.height) * 100;
                glare.style.background = `
                    radial-gradient(circle at ${glareX}% ${glareY}%, 
                    rgba(255,255,255,${this.config.maxGlare}) 0%, 
                    rgba(255,255,255,0) 60%)
                `;
                glare.style.opacity = '1';
            }
        }
    },

    handleMouseLeave(el) {
        el.style.transform = `
            perspective(${this.config.perspective}px)
            rotateX(0deg)
            rotateY(0deg)
            scale3d(1, 1, 1)
        `;
        
        const glare = el.querySelector('.tilt-glare');
        if (glare) {
            glare.style.opacity = '0';
        }
    },

    handleMouseEnter(el) {
        el.style.transition = 'none';
    }
};

// 自动初始化带 data-tilt 属性的元素
document.addEventListener('DOMContentLoaded', () => {
    const elements = document.querySelectorAll('[data-tilt]');
    if (elements.length > 0) {
        const maxTilt = parseInt(elements[0].dataset.tiltMax) || 15;
        TiltCard.init('[data-tilt]', { maxTilt });
    }
});

window.TiltCard = TiltCard;
