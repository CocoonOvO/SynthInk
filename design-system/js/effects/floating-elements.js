/**
 * FloatingElements - 浮动装饰元素
 * 在页面背景生成缓慢浮动的装饰元素
 * 
 * 使用：FloatingElements.init({ count: 5, shapes: ['circle', 'square'], colors: ['#fff'] })
 */

const FloatingElements = {
    config: {
        count: 5,
        shapes: ['circle', 'square', 'triangle'],
        minSize: 20,
        maxSize: 80,
        colors: ['rgba(255,255,255,0.03)'],
        container: 'body',
        zIndex: -1
    },

    elements: [],

    init(options = {}) {
        this.config = { ...this.config, ...options };
        
        // 检测减少动画偏好
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            return;
        }

        this.container = document.querySelector(this.config.container) || document.body;
        this.createElements();
        this.animate();
    },

    createElements() {
        for (let i = 0; i < this.config.count; i++) {
            const el = document.createElement('div');
            const size = this.random(this.config.minSize, this.config.maxSize);
            const shape = this.config.shapes[Math.floor(Math.random() * this.config.shapes.length)];
            const color = this.config.colors[Math.floor(Math.random() * this.config.colors.length)];
            
            el.style.cssText = `
                position: fixed;
                width: ${size}px;
                height: ${size}px;
                background: ${color};
                z-index: ${this.config.zIndex};
                pointer-events: none;
            `;

            // 根据形状设置
            if (shape === 'circle') {
                el.style.borderRadius = '50%';
            } else if (shape === 'triangle') {
                el.style.width = '0';
                el.style.height = '0';
                el.style.background = 'transparent';
                el.style.borderLeft = `${size/2}px solid transparent`;
                el.style.borderRight = `${size/2}px solid transparent`;
                el.style.borderBottom = `${size}px solid ${color}`;
            }

            // 初始位置和动画参数
            const element = {
                el: el,
                x: Math.random() * window.innerWidth,
                y: Math.random() * window.innerHeight,
                speedX: (Math.random() - 0.5) * 0.3,
                speedY: (Math.random() - 0.5) * 0.3,
                rotation: Math.random() * 360,
                rotationSpeed: (Math.random() - 0.5) * 0.2,
                opacity: Math.random() * 0.5 + 0.1
            };

            el.style.left = `${element.x}px`;
            el.style.top = `${element.y}px`;
            el.style.opacity = element.opacity;
            
            this.container.appendChild(el);
            this.elements.push(element);
        }
    },

    animate() {
        const update = () => {
            this.elements.forEach(item => {
                item.x += item.speedX;
                item.y += item.speedY;
                item.rotation += item.rotationSpeed;

                // 边界检测
                if (item.x < -100) item.x = window.innerWidth + 100;
                if (item.x > window.innerWidth + 100) item.x = -100;
                if (item.y < -100) item.y = window.innerHeight + 100;
                if (item.y > window.innerHeight + 100) item.y = -100;

                item.el.style.transform = `translate(${item.x}px, ${item.y}px) rotate(${item.rotation}deg)`;
            });

            requestAnimationFrame(update);
        };

        update();
    },

    random(min, max) {
        return Math.random() * (max - min) + min;
    },

    destroy() {
        this.elements.forEach(item => item.el.remove());
        this.elements = [];
    }
};

// 自动初始化
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('[data-floating]') ||
        document.body.dataset.floating !== 'false') {
        FloatingElements.init();
    }
});

window.FloatingElements = FloatingElements;
