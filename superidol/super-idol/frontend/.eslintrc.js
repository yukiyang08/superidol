module.exports = {
    root: true,
    env: {
        node: true,
        browser: true,
        es2021: true
    },
    extends: [
        'plugin:vue/vue3-essential',
        'eslint:recommended'
    ],
    parserOptions: {
        ecmaVersion: 2021
    },
    rules: {
        'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
        'no-debugger': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
        'vue/multi-word-component-names': 'off',
        'vue/no-v-model-argument': 'off',
        'vue/no-multiple-template-root': 'off',
        'vue/no-v-for-template-key': 'off',
        'vue/no-v-html': 'off',
        'vue/require-default-prop': 'off',
        'vue/require-prop-types': 'off',
        'vue/valid-v-model': 'off',
        'vue/valid-v-slot': 'off',
        'vue/valid-template-root': 'off',
        'vue/no-mutating-props': 'off',
        'vue/no-side-effects-in-computed-properties': 'off',
        'vue/no-unused-components': 'warn',
        'vue/no-unused-vars': 'warn',
        'vue/require-v-for-key': 'warn',
        'vue/valid-v-bind': 'warn',
        'vue/valid-v-on': 'warn',
        'vue/valid-v-show': 'warn',
        'vue/valid-v-if': 'warn',
        'vue/valid-v-else': 'warn',
        'vue/valid-v-else-if': 'warn',
        'vue/valid-v-for': 'warn',
        'vue/valid-v-text': 'warn',
        'vue/valid-v-html': 'warn',
        'vue/valid-v-once': 'warn',
        'vue/valid-v-pre': 'warn',
        'vue/valid-v-cloak': 'warn',
        'vue/valid-v-bind-sync': 'warn',
        'vue/valid-v-once': 'warn',
        'vue/valid-v-pre': 'warn',
        'vue/valid-v-cloak': 'warn',
        'vue/valid-v-bind-sync': 'warn'
    }
}; 