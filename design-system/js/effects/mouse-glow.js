/**
 * MouseGlow Effect - 鼠标跟随光晕
 * 鼠标移动时产生跟随的光晕效果
 * 
 * 使用：MouseGlow.init({ size: 200, blur: 50, opacity: 0.15 })
 */

const MouseGlow = {
    config: {
        size: 200,
        blur: 50,
        opacity: 0.15,
        color: 'var(--accent-primary)',
        smooth: 0.1
    },
    
    mouseX: 0,
    mouseY: 0,
    currentX: 0,
    currentY: 0,
    glow: null,
    rafId: null,

    init(options = {}) {
        this.config = { ...this.config, ...options };
        
        // 检测是否为触摸设备
        if (window.matchMedia('(pointer: coarse)').matches) {
            return; // 触摸设备不启用
        }

        this.createGlow();
        this.bindEvents();
        this.animate();
    },

    createGlow() {
        this.glow = document.createElement('div');
        this.glow.className = 'mouse-glow';
        this.glow.style.cssText = `
            position: fixed;
            width: ${this.config.size}px;
            height: ${this.config.size}px;
            border-radius: 50%;
            background: radial-gradient(circle, ${this.getColor()} 0%, transparent 70%);
            filter: blur(${this.config.blur}px);
            opacity: 0;
            pointer-events: none;
            z-index: 9999;
            transform: translate(-50%, -50%);
            transition: opacity 0.3s ease;
        `;
        document.body.appendChild(this.glow);
    },

    getColor() {
        // 获取当前主题色
        const style = getComputedStyle(document.body);
        const accent = style.getPropertyValue('--accent-primary').trim();
        return accent || this.config.color;
    },

    bindEvents() {
        document.addEventListener('mousemove', (e) => {
            this.mouseX = e.clientX;
            this.mouseY = e.clientY;
            
            if (this.glow) {
                this.glow.style.opacity = this.config.opacity;
            }
        });

        document.addEventListener('mouseleave', () => {
            if (this.glow) {
                this.glow.style.opacity = '0';
            }
        });

        // 监听主题变化
        window.addEventListener('themechange', () => {
            if (this.glow) {
                this.glow.style.background = `radial-gradient(circle, ${this.getColor()} 0%, transparent 70%)`;
            }
        });
    },

    animate() {
        const update = () => {
            // 平滑跟随
            this.currentX += (this.mouseX - this.currentX) * this.config.smooth;
            this.currentY += (this.mouseY - this.currentY) * this.config.smooth;

            if (this.glow) {
                this.glow.style.left = `${this.currentX}px`;
                this.glow.style.top = `${this.currentY}px`;
            }

            this.rafId = requestAnimationFrame(update);
        };

        update();
    },

    destroy() {
        if (this.rafId) {
            cancelAnimationFrame(this.rafId);
        }
        if (this.glow) {
            this.glow.remove();
        }
    }
};

// 自动初始化
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('[data-mouse-glow]') || 
        document.body.dataset.mouseGlow !== 'false') {
        MouseGlow.init();
    }
});

window.MouseGlow = MouseGlow;
