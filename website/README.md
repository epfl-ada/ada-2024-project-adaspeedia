At each commit, build is done and published here : adaspeedia.pages.dev

## ⚡ Quick Start

```bash
# Clone the repository
git clone https://github.com/agentc-app/astro-shadcn.git

# Navigate to project
cd astro-shadcn

# Install dependencies
npm install

# Start development server
npm run dev
```

Visit `http://localhost:4321` - You're ready to go! 🎉


## 🚀 Development Workflow

1. **Start Development**
   ```bash
   npm run dev
   ```

2. **Using React Components in Astro**
   ```astro
   ---
   // Always add client:load for interactive components
   import { Dialog } from "@/components/ui/dialog"
   ---
   
   <Dialog client:load>
     <!-- Dialog content -->
   </Dialog>
   ```

3. **Build for Production**
   ```bash
   npm run build
   npm run preview # Test the production build
   ```

## 🔍 Troubleshooting

### Common Issues Solved

✅ **Component Hydration**: All interactive components use `client:load`
✅ **Build Warnings**: Suppressed in configuration
✅ **Path Aliases**: Pre-configured for easy imports
✅ **React Integration**: Properly set up for Shadcn

### Quick Fixes

1. **Clear Cache**
   ```bash
   rm -rf dist node_modules .astro
   npm install
   ```

2. **Restart Dev Server**
   ```bash
   # Kill the dev server and restart
   npm run dev
   ```

## 💡 Pro Tips

1. **Component Usage in Astro**
   ```astro
   ---
   // Always import in the frontmatter
   import { Button } from "@/components/ui/button"
   ---
   
   <!-- Use in template -->
   <Button client:load>Click me!</Button>
   ```

2. **Styling with Tailwind**
   ```astro
   <div class="dark:bg-slate-800">
     <Button class="m-4">Styled Button</Button>
   </div>
   ```

3. **Layout Usage**
   ```astro
   ---
   import Layout from '../layouts/Layout.astro';
   ---
   
   <Layout title="Home">
     <!-- Your content -->
   </Layout>
   ```