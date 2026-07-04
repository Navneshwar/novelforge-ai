import React from 'react';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Underline from '@tiptap/extension-underline';
import TextAlign from '@tiptap/extension-text-align';
import Placeholder from '@tiptap/extension-placeholder';

const MenuBar = ({ editor }) => {
  if (!editor) return null;

  const btnStyle = (isActive) => ({
    padding: '0.35rem 0.6rem',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '0.85rem',
    fontWeight: isActive ? '700' : '500',
    background: isActive ? '#6c63ff' : 'transparent',
    color: isActive ? '#fff' : '#a0a0b8',
    transition: 'all 0.15s',
    minWidth: '30px',
  });

  const divider = <div style={{ width: '1px', background: '#2a2a3a', margin: '0 0.3rem', alignSelf: 'stretch' }} />;

  return (
    <div className="editor-toolbar">
      {/* Text formatting */}
      <button
        style={btnStyle(editor.isActive('bold'))}
        onClick={() => editor.chain().focus().toggleBold().run()}
        title="Bold (Ctrl+B)"
      >
        <strong>B</strong>
      </button>
      <button
        style={btnStyle(editor.isActive('italic'))}
        onClick={() => editor.chain().focus().toggleItalic().run()}
        title="Italic (Ctrl+I)"
      >
        <em>I</em>
      </button>
      <button
        style={btnStyle(editor.isActive('underline'))}
        onClick={() => editor.chain().focus().toggleUnderline().run()}
        title="Underline (Ctrl+U)"
      >
        <u>U</u>
      </button>
      <button
        style={btnStyle(editor.isActive('strike'))}
        onClick={() => editor.chain().focus().toggleStrike().run()}
        title="Strikethrough"
      >
        <s>S</s>
      </button>

      {divider}

      {/* Headings */}
      <button
        style={btnStyle(editor.isActive('heading', { level: 1 }))}
        onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
        title="Heading 1"
      >
        H1
      </button>
      <button
        style={btnStyle(editor.isActive('heading', { level: 2 }))}
        onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
        title="Heading 2"
      >
        H2
      </button>
      <button
        style={btnStyle(editor.isActive('heading', { level: 3 }))}
        onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}
        title="Heading 3"
      >
        H3
      </button>

      {divider}

      {/* Lists */}
      <button
        style={btnStyle(editor.isActive('bulletList'))}
        onClick={() => editor.chain().focus().toggleBulletList().run()}
        title="Bullet List"
      >
        •≡
      </button>
      <button
        style={btnStyle(editor.isActive('orderedList'))}
        onClick={() => editor.chain().focus().toggleOrderedList().run()}
        title="Ordered List"
      >
        1.
      </button>
      <button
        style={btnStyle(editor.isActive('blockquote'))}
        onClick={() => editor.chain().focus().toggleBlockquote().run()}
        title="Blockquote"
      >
        ❝
      </button>

      {divider}

      {/* Alignment */}
      <button
        style={btnStyle(editor.isActive({ textAlign: 'left' }))}
        onClick={() => editor.chain().focus().setTextAlign('left').run()}
        title="Align Left"
      >
        ≡←
      </button>
      <button
        style={btnStyle(editor.isActive({ textAlign: 'center' }))}
        onClick={() => editor.chain().focus().setTextAlign('center').run()}
        title="Align Center"
      >
        ≡↔
      </button>
      <button
        style={btnStyle(editor.isActive({ textAlign: 'right' }))}
        onClick={() => editor.chain().focus().setTextAlign('right').run()}
        title="Align Right"
      >
        →≡
      </button>

      {divider}

      {/* Undo/Redo */}
      <button
        style={btnStyle(false)}
        onClick={() => editor.chain().focus().undo().run()}
        disabled={!editor.can().undo()}
        title="Undo (Ctrl+Z)"
      >
        ↩
      </button>
      <button
        style={btnStyle(false)}
        onClick={() => editor.chain().focus().redo().run()}
        disabled={!editor.can().redo()}
        title="Redo (Ctrl+Shift+Z)"
      >
        ↪
      </button>

      {divider}

      {/* Horizontal rule */}
      <button
        style={btnStyle(false)}
        onClick={() => editor.chain().focus().setHorizontalRule().run()}
        title="Horizontal Rule"
      >
        ―
      </button>
    </div>
  );
};

function RichTextEditor({ content, onUpdate, placeholder }) {
  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        heading: { levels: [1, 2, 3] },
      }),
      Underline,
      TextAlign.configure({
        types: ['heading', 'paragraph'],
      }),
      Placeholder.configure({
        placeholder: placeholder || 'Start writing...',
      }),
    ],
    content: content || '',
    onUpdate: ({ editor }) => {
      if (onUpdate) {
        onUpdate(editor.getHTML());
      }
    },
    editorProps: {
      attributes: {
        class: 'rich-editor-content',
      },
    },
  });

  // Calculate word count from editor text
  const wordCount = editor ? editor.getText().split(/\s+/).filter(Boolean).length : 0;
  const charCount = editor ? editor.getText().length : 0;

  return (
    <div className="rich-editor-wrapper">
      <MenuBar editor={editor} />
      <div className="rich-editor-body">
        <EditorContent editor={editor} />
      </div>
      <div className="rich-editor-statusbar">
        <span>{wordCount} words</span>
        <span>{charCount} characters</span>
      </div>
    </div>
  );
}

export default RichTextEditor;
