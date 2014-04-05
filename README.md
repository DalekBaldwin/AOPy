AOPy
====

AOPy is a small but powerful aspect-oriented programming utility for Python designed for productive, pedagogical, and evangelical purposes.

Background and Motivation
-------------------------
(You can find plenty of good introductions to AOP in general elsewhere on the web. This section focuses on its usefulness in Python.)

I began this project after I realized I couldn't find any easy-to-use AOP solutions in Python. One library called Aspyct seemed promising, but the original source code had disappeared down an interweb black hole and, strangely, the author saw no value in it:

> ...what aspyct allows you to do is actually quite easy with python! Basically, aspyct did two things:

> 1. wrap functions with custom behavior, like transaction handling or security enforcement;
> 2. cut through modules and classes to apply these behaviors.

> The first thing is easy to do with decorators.

> The second thing is a bit more tricky to accomplish, but is based on a simple fact: you can replace functions and methods at runtime. This is called 'monkey patching'.

It was odd to see that someone could implement AOP in Python but still not see what it offers above and beyond the built-in features of the language. It's like seeing someone ask why we don't write all our software in assembly language.

Decorators are useful, but when you apply a decorator, whatever concept the decorator represents is lexically attached to a single function definition in isolation from the rest of the codebase. There's no facility in the language for intelligently composing more complex behavior on top of it. If you're going to change some behavior involving a decorator across many methods or many files, you still have to grep for the decorator name to find every place in the code where it is applied, and you may have to modify all of those places too. This is time-consuming and error-prone, especially if you are using temporary debugging statements or making tentative and exploratory changes. You can comment decorators out and uncomment them back in all day long, and no matter how good you get at it, someday you're going to embarrass yourself by giving a presentation and having to tell the audience, "Oops, all of that debugging clutter shouldn't be there." (You've done it before. Admit it.) Worse, the scope of the decorator's application can only be defined [extensionally](http://en.wikipedia.org/wiki/Extension_(semantics)), so when you come back five months later to do some code archaeology, you have to ask, "What do all these decorated functions have in common?" Aspects let you define regions of your program inten**s**ionally which better expresses your inten**t**ion and naturally leads to more self-documenting code.

The story for monkey-patching is similar. Monkey-patching is essentially what AOPy does, under the hood. But if you have to augment the behavior of many different functions that are systematically related, wouldn't you rather use a more expressive and manageable abstraction than a list of assignment statements?

How It Works
------------
Aspects are defined as classes inheriting from the class `AspectBase`. Each aspect base class encapsulates logic for determining how a particular collection of functions and methods should map to a pointcut -- that is, in what situations a piece of advice should actually apply to one of those callables based on the dynamic context. Each derived aspect class contains an attribute called `targets` which is a list of all functions/methods the aspect's advice should wrap, and the aspect's `__call__` method determines when its advice should apply. This way, AOPy requires no special syntax, file format, or DSL. You express your aspects in the language you're already thinking in: plain Python.

For each function/method in `targets`, the aspect class is instantiated to create a callable object that replaces either the original function/method or another aspect instance already wrapping that function/method. This allows for the dynamic enabling and disabling of aspects. When an aspect is enabled, it becomes the outermost wrapping on every target to which it applies; its `before_advice`, when applicable, runs first before all other aspects' `before_advice`, and its `after_advice` and `after_exception_advice` run last. When an aspect in the middle of the wrapping chain on a given target is disabled, it is simply removed from the wrapping chain.

The first time an aspect is enabled on a callable, that callable is registered by identity in a dictionary associating it with its module object, class object (if it is a method), and name. Modules, classes, functions, and methods defined in the code should not be replaced by any other mechanism. This should still allow for interactive development of both core functionality and aspects via a REPL as long as all aspects are uninstalled (with `reset_all`) before replacing any callables that have previously been augmented by aspects. If modules or classes are replaced, the `targets` attribute on each aspect should be recomputed.

You can create new aspect base classes to create new semantics for constructing pointcuts from `targets` or to keep track of additional introspective information.

You can define an aspect's target callables extensionally (by naming functions and methods individually), intensionally (by creating expressions that return functions and methods satisfying certain properties), or as a mixture of the two. For instance, say you're debugging a GUI application and you have reason to suspect that some unintended behavior is due to you, the lowly framework user, and not due to the people who have been refining the framework for years. You might want to write an aspect to trace calls to methods you have defined on GUI widgets you have subclassed to create your application-specific widgets, but not the methods that are automatically inherited from the GUI framework's superclasses, which make up the majority of calls triggered by all kinds of events you didn't even know were being monitored. After spending a few minutes refreshing yourself on Python's introspection tools, you can come up with an expression to zero in on precisely the methods you are interested in, based on the constraints just described.

AOPy has only been tested with Python 2.7.

Example
-------

Imagine we have a program for drawing shapes with a compositional object model. We draw a square, consisting of four lines of two points each, and also a line that is not part of any larger shape, and also a point which is not part of any line. If we move the single point, we want to redraw the screen; however, we do not want to redraw the screen after moving each point in the process of moving the line it is part of, or after moving each line and each point on that line in the process of moving the square, etc. We need an implementation of the observer pattern that is aware of the dynamic context so that the screen is redrawn only after the parent object and all of its children have been updated with their new positions. See the /examples directory to see how AOPy can do this without requiring any shape class to refer to the screen update code, and while seamlessly integrating debugging aspects as well.

The Frequently Asked Question
-----------------------------

Q: But this is breaks the encapsulation in my program's design! If I make a change here, I won't know that it's affected by some piece of code over there!

A: http://www.youtube.com/watch?v=cq7wpLI0hco&t=45m35s [45:35-47:45]



*Note that aspects can also be usefully combined with decorators. If you add a line of code to the decorator that adds its decoratee to a dictionary, the expression for building an aspect's `targets` attribute can simply query that dictionary. This also eases the task of refactoring code from using decorators to using aspects. If you're still uneasy about this whole AOP thing and you think there are places where anybody who's poking around your codebase should always know that some spooky action at a distance is going on so they won't mess things up, you can use this strategy pretty seamlessly.