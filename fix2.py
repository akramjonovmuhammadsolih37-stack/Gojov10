f = open('userbot_panel.html', 'r')
c = f.read()
f.close()

old = """  } catch (e) {
    return null;
  }
}"""

new = """  } catch (e) {
    console.error('API xato:', e);
    alert('Xato: ' + e.message);
    return null;
  }
}"""

c = c.replace(old, new, 1)
f = open('userbot_panel.html', 'w')
f.write(c)
f.close()
print('OK')
