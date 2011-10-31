********
CheckBox
********

.. autoclass:: manygui.CheckBox

        CheckBox is a kind of button, and thus will also generate 'click' and
        'default' events when clicked. But in addition, each CheckBox has a
        Boolean attribute on, which is toggled each time the box is clicked.
        The state of the CheckBox can be altered by assigning to this
        attribute.

        .. attribute:: on

                The `on` property will be automatically modified (as per the MVC
                mechanism) when the user clicks the CheckBox. This will also cause the
                CheckBox to send a click and a defaultevent.

                The `on` attribute is a useful place to use a BooleanModel.

