/**
 * Typewriter Effect - 打字机效果
 * 让文字像打字一样逐个显示
 * 
 * 使用：Typewriter.init('.selector', { speed: 50, delay: 0 })
 */

const Typewriter = {
    init(selector, options = {}) {
        const elements = document.querySelectorAll(selector);
        const config = {
            speed: options.speed || 50,
            delay: options.delay || 0,
            cursor: options.cursor !== false,
            cursorChar: options.cursorChar || '|'
        };

        elements.forEach(el => {
            const text = el.textContent;
            el.textContent = '';
            el.style.opacity = '1';
            
            if (config.cursor) {
                const cursor = document.createElement('span');
                cursor.className = 'typewriter-cursor';
                cursor.textContent = config.cursorChar;
                cursor.style.cssText = `
                    display: inline-block;
                    animation: typewriter-blink 1s infinite;
                    color: var(--accent-primary);
                    margin-left: 2px;
                `;
                el.appendChild(cursor);
            }

            setTimeout(() => {
                this.type(el, text, config.speed, 0);
            }, config.delay);
        });

        // 添加光标闪烁动画
        if (!document.getElementById('typewriter-style')) {
            const style = document.createElement('style');
            style.id = 'typewriter-style';
            style.textContent = `
                @keyframes typewriter-blink {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0; }
                }
            `;
            document.head.appendChild(style);
        }
    },

    type(el, text, speed, index) {
        const cursor = el.querySelector('.typewriter-cursor');
        
        if (index < text.length) {
            const char = document.createTextNode(text[index]);
            if (cursor) {
                el.insertBefore(char, cursor);
            } else {
                el.appendChild(char);
            }
            setTimeout(() => this.type(el, text, speed, index + 1), speed);
        }
    }
};

// 自动初始化带 data-typewriter 属性的元素
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-typewriter]').forEach(el => {
        const speed = parseInt(el.dataset.typewriterSpeed) || 50;
        const delay = parseInt(el.dataset.typewriterDelay) || 0;
        Typewriter.init(el, { speed, delay });
    });
});

window.Typewriter = Typewriter;
